import statistics
import spotipy
from PIL import Image, ImageDraw

def getTrackIDs(token):
    """
    Fetches a user's top track IDs from Spotify using the provided token.

    Args:
        token (str): Spotify access token.

    Returns:
        tuple: A tuple containing the list of track IDs and the current user's username, 
               or (None, None) if an error occurs.
    """
    try:
        sp = spotipy.Spotify(auth=token)
        user_top_tracks = sp.current_user_top_tracks(limit=50, offset=0, time_range='long_term')
        track_ids = [track['id'] for track in user_top_tracks['items']]
        current_username = sp.current_user()['display_name']
        return track_ids, current_username
    except spotipy.exceptions.SpotifyException as e:
        print(f"An error occurred: {e}")
        return None, None

def getAudioFeat(token, track_ids):
    """
    Retrieves audio features for given track IDs from Spotify.

    Args:
        token (str): Spotify access token.
        track_ids (list): List of Spotify track IDs.

    Returns:
        list: List of dictionaries containing extracted audio features for each track,
              or an empty list if an error occurs.
    """
    try:
        sp = spotipy.Spotify(auth=token)
        audio_features = sp.audio_features(track_ids)
        
        extracted_features = []
        for features in audio_features:
            if features:
                extracted_features.append({
                    'id': features['id'],
                    'danceability': features['danceability'],
                    'energy': features['energy'],
                    'valence': features['valence'],
                    'key': features['key'],
                    'mode': features['mode'],
                    'acousticness': features['acousticness'],
                    'loudness': features['loudness']
                })
        return extracted_features
    except spotipy.exceptions.SpotifyException as e:
        print(f"An error occurred: {e}")
        return []

def calculate_median_features(audio_features):
    """
    Calculates the median values of specified audio features.

    Args:
        audio_features (list): List of dictionaries with audio features.

    Returns:
        dict: Dictionary of median values of specified audio features.
    """
    feature_keys = ['danceability', 'energy', 'valence', 'acousticness', 'loudness']
    return {key: statistics.median([track[key] for track in audio_features]) for key in feature_keys}

def normalize_features(median_features):
    """
    Normalizes specified audio features for better visualization.

    Args:
        median_features (dict): Dictionary of median values of audio features.

    Returns:
        dict: Dictionary of normalized audio features.
    """
    return {
        'Energy': median_features['energy'] * 100,
        'Positivity': median_features['valence'] * 100,
        'Grooviness': median_features['danceability'] * 100,
        'Naturalness': median_features['acousticness'] * 100,
        'Intensity': ((median_features['loudness'] + 60) / 60) * 100
    }

def createRadarChart(audio_features):
    """
    Prepares data for radar chart visualization based on audio features.

    Args:
        audio_features (list): List of dictionaries with audio features.

    Returns:
        dict: Dictionary of normalized audio features suitable for radar chart plotting.
    """
    median_features = calculate_median_features(audio_features)
    return normalize_features(median_features)

def energy_valence_RGB(audio_features):
    """
    Determines a color based on the median energy and valence of audio features.
    """
    energies = [features['energy'] for features in audio_features]
    valences = [features['valence'] for features in audio_features]
    
    median_energy = round(statistics.median(energies), 2) 
    median_valence = round(statistics.median(valences), 2)
    
    q_colors = {
        "Q1": (51, 51, 255),    # Blue
        "Q2": (73, 254, 54),    # Green
        "Q3": (156, 43, 154),  # Purple
        "Q4": (255, 51, 51)     # Red
    }
        
    return convertToRGB(median_energy, median_valence, q_colors)

def convertToRGB(energy, valence, q_colors):
    """
    Converts energy and valence values to an RGB color.
    """
    weights = {
        "Q1": (1 - energy) * valence if energy < 0.5 and valence > 0.5 else 0,    # blue
        "Q2": energy * valence if energy > 0.5 and valence > 0.5 else 0,          # green
        "Q3": (1 - energy) * (1 - valence) if energy < 0.5 and valence < 0.5 else 0, # purple
        "Q4": energy * (1 - valence) if energy > 0.5 and valence < 0.5 else 0     # red
    }

    total_weight = sum(weights.values())
    scaled_weights = {q: (w ** 0.5) / total_weight for q, w in weights.items()} if total_weight > 0 else weights

    base_saturation = 30
    R = sum(q_colors[q][0] * scaled_weights[q] for q in q_colors) + base_saturation
    G = sum(q_colors[q][1] * scaled_weights[q] for q in q_colors) + base_saturation
    B = sum(q_colors[q][2] * scaled_weights[q] for q in q_colors) + base_saturation

    return int(min(255, max(0, R))), int(min(255, max(0, G))), int(min(255, max(0, B)))

def keyRGB(audio_features):
    """
    Determines the RGB color based on the most common musical key.
    """
    keys = [features['key'] for features in audio_features]
    
    try:
        key_mode = statistics.mode(keys)
    except:
        key_mode = keys[0]  # if no mode is found
    
    key_colors = {
        -1: (255, 255, 255),  # No Key: White
        0: (32, 178, 170),    # C: Green
        1: (100, 253, 207),   # C♯/D♭: Green-Cyan
        2: (159, 230, 231),   # D: Cyan
        3: (100, 206, 252),   # D♯/E♭: Blue-Cyan
        4: (69, 156, 236),    # E: Blue
        5: (192, 136, 230),   # F: Purple
        6: (253, 132, 144),   # F♯/G♭: Red
        7: (247, 183, 165),   # G: Red-Orange
        8: (245, 199, 126),   # G♯/A♭: Orange
        9: (255, 208, 87),    # A: Orange-Yellow
        10: (252, 240, 136),  # A♯/B♭: Yellow
        11: (205, 249, 138)   # B: Green-Yellow
    }

    return key_colors.get(key_mode, (255, 255, 255))

def createAura(center_color, edge_color, size=(665,665), gamma=1.3):
    """
    Creates a radial gradient image representing the user's music taste.
    """
    width, height = size
    center_x, center_y = width // 2, height // 2
    max_radius = min(center_x, center_y)

    radial_gradient = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(radial_gradient)

    for y in range(height):
        for x in range(width):
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            factor = distance / max_radius
            factor = min(1, factor ** gamma)

            color = [int(center_color[i] * (1 - factor) + edge_color[i] * factor) for i in range(3)]
            if distance <= max_radius:
                draw.point((x, y), tuple(color + [255]))

    return radial_gradient

def auraBg(rgb_color, size=(265,265), factor=0.06):
    """
    Creates a background image for the aura.
    """
    r, g, b = rgb_color
    lighter_color = (min(255, int(r + 255 * factor)), 
                     min(255, int(g + 255 * factor)), 
                     min(255, int(b + 255 * factor)))

    img = Image.new('RGB', size, lighter_color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, size[0], size[1]], fill=lighter_color)

    return img

def getValenceAdj(audio_features):
    """
    Determines the adjective that describes the median valence of audio features.

    Args:
        audio_features (list): List of dictionaries containing audio features.

    Returns:
        str: Adjective corresponding to the median valence.
    """
    valences = [features['valence'] for features in audio_features]
    median_valence = round(statistics.median(valences), 2)

    valence_categories = {
        (0.00, 0.10): "Sorrowful",
        (0.10, 0.20): "Gloomy",
        (0.20, 0.30): "Melancholic",
        (0.30, 0.40): "Somber",
        (0.40, 0.50): "Wistful",
        (0.50, 0.60): "Neutral",
        (0.60, 0.70): "Content",
        (0.70, 0.80): "Cheerful",
        (0.80, 0.90): "Joyful",
        (0.90, 1.00): "Ecstatic"
    }
    
    for (lower_bound, upper_bound), category in valence_categories.items():
        if lower_bound <= median_valence <= upper_bound:
            return category

    return "Mysterious"  # default category if median valence is not found

def getKeyAdj(audio_features):
    """
    Determines the adjective that describes the most common key in audio features.

    Args:
        audio_features (list): List of dictionaries containing audio features.

    Returns:
        str: Adjective corresponding to the most common key.
    """
    keys = [features['key'] for features in audio_features]
    
    try:
        key_mode = statistics.mode(keys)
    except statistics.StatisticsError:
        key_mode = keys[0]  # if no mode is found
    
    key_adjectives = {
        -1: "Varied",
        0: "Pure",
        1: "Introspective",
        2: "Lively",
        3: "Majestic",
        4: "Vibrant",
        5: "Soulful",
        6: "Pensive",
        7: "Mellow",
        8: "Sentimental",
        9: "Spirited",
        10: "Dramatic",
        11: "Bold"
    }
    
    return key_adjectives.get(key_mode, "Varied")

def features_to_stars(audio_features):
    """
    Converts audio features into a star rating representation.

    Args:
        audio_features (list): List of dictionaries containing audio features.

    Returns:
        dict: Dictionary mapping feature names to star ratings.
    """
    median_features = calculate_median_features(audio_features)
    normalized_features = normalize_features(median_features)
    
    star_representation = {}
    for feature, value in normalized_features.items():
        stars = '✦' * int(round(value / 20))
        star_representation[feature] = stars
    
    return star_representation
