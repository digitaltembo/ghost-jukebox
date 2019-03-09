from db import query_one

# these keys are used a bunch I guess 
SPOTIFY_DEVICE_ID = 'SPOTIFY_DEVICE_ID'
SPOTIFY_ACCESS_TOKEN = 'SPOTIFY_ACCESS_TOKEN'
SPOTIFY_REFRESH_TOKEN = 'SPOTIFY_REFRESH_TOKEN'
SPOTIFY_TOKEN_EXPIRATION = 'SPOTIFY_TOKEN_EXPIRATION'

def get_info(key):
    return query_one('SELECT value FROM info WHERE key = ?', [key])

def set_info(key, value):
    if(get_info(key)):
        query_one('UPDATE info SET value = ? WHERE key = ?', [str(value), key])
    else:
        query_one('INSERT INTO info (key, value) VALUES ?, ?', [key, str(value)])

def set_infos(info_dict):
    for key in info_dict:
        set_info(key, info_dict[key])


