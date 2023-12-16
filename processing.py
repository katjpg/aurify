import statistics
import spotipy

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