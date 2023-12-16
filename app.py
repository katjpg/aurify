import time
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, redirect, session, render_template, url_for, make_response
from flask_apscheduler import APScheduler
import os 
from datetime import datetime, timedelta
import logging
import uuid
import aura_visualization
from dotenv import load_dotenv

# ===================== CONSTANTS =====================

load_dotenv() # load environment variables from .env file

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SESSION_TOKEN = os.getenv('SESSION_TOKEN')
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')

# api version v1 
SPOTIFY_BASE_URL = "https://api.spotify.com/v1/"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_SCOPE = "user-top-read user-library-read"


# ===================== SPOTIFY OAUTH =====================

def spotify_oauth():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID, 
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=url_for("redirectPage",_external=True), 
        scope=SPOTIFY_SCOPE
        )

# ===================== APP =====================

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
scheduler = APScheduler()

# ===================== SCHEDULER =====================

logging.basicConfig(level=logging.INFO)

def cleanup_old_images():
    logging.info("Running cleanup_old_images function")  # Log when the function starts
    now = datetime.now()
    for filename in os.listdir('static'):
        # Check if '_aura' is in the filename
        if '_aura' in filename:
            filepath = os.path.join('static', filename)
            if os.path.getmtime(filepath) < (now - timedelta(minutes=2)).timestamp():
                os.remove(filepath)
                logging.info(f"Deleted file: {filepath}")


# initialize the scheduler
scheduler.init_app(app)
scheduler.start()

# schedule the cleanup task to run every 2 minutes
scheduler.add_job(id='Scheduled Cleanup', func=cleanup_old_images, trigger='interval', minutes=2)

# ===================== ROUTES =====================
@app.route('/')
def index():
    return render_template('index.html')

# ================== LOGIN PAGE ==================
@app.route('/login')
def login():
    sp_oauth = spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

# ================== REDIRECT PAGE ==================
@app.route('/redirect')
def redirectPage():
    sp_oauth = spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[SESSION_TOKEN] = token_info
    session.modified = True 
    return redirect(url_for('profile', _external=True))

def get_token():
    token_info = session.get(SESSION_TOKEN)
    if not token_info:
        raise ValueError("Spotify access token is missing from the session.")
    
    now = int(time.time())
    is_expired = token_info.get('expires_at') - now < 60
    if (is_expired):
        sp_oauth = spotify_oauth()
        try:
            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
        except:
            raise ValueError("Failed to refresh access token.")

    return token_info

# ================== ABOUT PAGE ==================

@app.route('/about')
def about():
    return render_template('about.html')

# ================== CONTACT PAGE ==================

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ================== PRIVACY PAGE ==================

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# ================== PROFILE PAGE ==================

@app.route('/profile')
def profile():
    try:
        # retrieve the Spotify access token from the session
        token_info = get_token()  
        if not token_info:
            return redirect(url_for('login', _external=True))
        
        # fetch user's top tracks and their audio features
        track_ids, current_username = aura_visualization.getTrackIDs(token_info['access_token'])
        if track_ids is None:
            raise ValueError("Error fetching track IDs.")
        audio_features = aura_visualization.getAudioFeat(token_info['access_token'], track_ids)

        # calculate energy-valence and key colors
        ev_rgb_color = aura_visualization.energy_valence_RGB(audio_features)
        key_rgb_color = aura_visualization.keyRGB(audio_features)
        
        # get adjectives for key and valence
        key_adj = aura_visualization.getKeyAdj(audio_features)
        valence_adj = aura_visualization.getValenceAdj(audio_features)

        # create the aura image
        aura_image = aura_visualization.createAura(ev_rgb_color, key_rgb_color, (665, 665), 1.3)
        aura_background = aura_visualization.auraBg(key_rgb_color, (450, 450), 0.06)

        # resize and position aura_image
        smaller_size = (350, 350)
        aura_image = aura_image.resize(smaller_size)
        x_position = (aura_background.size[0] - smaller_size[0]) // 2
        y_position = (aura_background.size[1] - smaller_size[1]) // 2
        aura_background.paste(aura_image, (x_position, y_position), aura_image)

        # save the final combined image
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4()
        aura_image_path = f"static/{current_username}_aura_{timestamp}_{unique_id}.png"
        aura_background.save(aura_image_path)

        # prepare additional data for the profile page
        radar_data = aura_visualization.createRadarChart(audio_features)
        plot_color_rgba = 'rgba({0}, {1}, {2}, 1)'.format(*key_rgb_color)
        ev_rgb_color = 'rgb({0}, {1}, {2})'.format(*ev_rgb_color)
        feature_stars = aura_visualization.features_to_stars(audio_features)
        
        # render the profile page with the data
        response = make_response(render_template('profile.html', 
                                                 aura_image_url=aura_image_path, 
                                                 radar_data=radar_data, 
                                                 plot_color_rgba=plot_color_rgba, 
                                                 feature_stars=feature_stars, 
                                                 key_adj=key_adj, 
                                                 valence_adj=valence_adj,
                                                 ev_rgb_color=ev_rgb_color))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    except Exception as e:
        print(f"An error occurred: {e}")
        return redirect(url_for('login', _external=True))

if __name__ == '__main__':
    app.run(debug=False) 
