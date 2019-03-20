import os

def get(env_variable, default):
    if env_variable in os.environ:
        return os.environ[env_variable]
    else:
        return default

username = get('GHOST_JUKEBOX_UNAME', 'admin')
password = get('GHOST_JUKEBOX_PSWD',  'password')

spotify_client = get('GHOST_SPOTIFY_CLIENT', 'client')
spotify_secret = get('GHOST_SPOTIFY_SECRET', 'secret')

host = get('GHOST_HOST', '0.0.0.0')

db_path = get('GHOST_DB_PATH', 'model.db')

upload_folder = get('GHOST_UPLOAD_DIR', '~/')