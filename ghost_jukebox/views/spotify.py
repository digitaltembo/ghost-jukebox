from flask import Flask, request, redirect, url_for, render_template
from io import BytesIO
from time import sleep
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth

from ghost_jukebox import app, auth, conf
from ghost_jukebox.models import info 

SPOTIFY_AUTHORIZE_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL     = 'https://accounts.spotify.com/api/token'

SCOPES = [
    'user-modify-playback-state',
    'user-read-playback-state',
    'user-read-recently-played',
    'playlist-read-private',
    'user-read-currently-playing'
] 


def spotify_url(endpoint):
    return 'https://api.spotify.com/v1/{}'.format(endpoint)

def get_expiration_time(expires_in):
    return (datetime.now() + timedelta(seconds=expires_in)).timestamp()


@app.route('/spotify/login')
@auth.login_required
def authorize():

    request_params = {
        'client_id'     : conf.spotify_client,
        'response_type' : 'code',
        'redirect_uri'  : 'https://{}{}'.format(conf.host, url_for('callback')),
        'scope'         : ' '.join(SCOPES)
    }

    url = requests.Request('GET', SPOTIFY_AUTHORIZE_URL, params=request_params).prepare().url

    return redirect(url)

@app.route('/spotify/callback')
def callback():
    access_code = request.args.get('code','')
    if access_code:
        payload = {
            'grant_type'   : 'authorization_code',
            'code'         : access_code,
            'redirect_uri' : 'https://{}{}'.format(conf.host, url_for('callback'))
        }

        token_response = requests.post(
            SPOTIFY_TOKEN_URL,
            data=payload,
            auth=HTTPBasicAuth(conf.spotify_client, conf.spotify_secret)
        )
        token_info = {}
        j = token_response.json()
        set_token_from_json(j)
        return 'COOOL'
    else:
        error_code = request.args.get('error','Unknown Reason')
        return 'blah'

@app.route('/spotify/api/<method>/<path:endpoint>')
@auth.login_required
def forward_spotify_call(method, endpoint):
    access_token = get_access_token()
    if not access_token:
        return 'blah'
    headers = {"Authorization": "Bearer {}".format(access_token)}

    index = request.url.find('?')
    get_parameters = '' if index == -1 else request.url[index:]
    url = spotify_url(endpoint) + get_parameters

    response = None

    if method == 'POST':
        response = requests.post(url, data=request.get_json(), headers=headers, stream=True)
    elif method == 'GET':
        response = requests.get(url, data=request.get_json(), headers=headers, stream=True)
    elif method == 'PUT':
        response = requests.put(url, data=request.get_json(), headers=headers, stream=True)
    elif method == 'DELETE':
        response = requests.delete(url, data=request.get_json(), headers=headers, stream=True)

    if response == None:
        return 'blah'
    return (response.raw.read(), response.status_code, response.headers.items())

def get_access_token():
    access_token  = info.get_info(info.SPOTIFY_ACCESS_TOKEN)
    
    if not access_token:
        return False 
    else:
        refresh_token = info.get_info(info.SPOTIFY_REFRESH_TOKEN)
        expiration    = datetime.fromtimestamp(float(info.get_info(info.SPOTIFY_TOKEN_EXPIRATION)))

        if datetime.now() < expiration:
            return access_token
        else:
            payload = {
                'grant_type'   : 'refresh_token',
                'refresh_token': refresh_token
            }

            token_response = requests.post(
                SPOTIFY_TOKEN_URL,
                data=payload,
                auth=HTTPBasicAuth(conf.spotify_client, conf.spotify_secret)
            )
            j = token_response.json()
            set_token_from_json(j)
            return j['access_token']

def set_token_from_json(token_json):
    info_dict = {
        info.SPOTIFY_ACCESS_TOKEN:     token_json['access_token'],
        info.SPOTIFY_TOKEN_EXPIRATION: get_expiration_time(token_json['expires_in'])
    }
    if 'refresh_token' in token_json:
        info_dict[info.SPOTIFY_REFRESH_TOKEN] = token_json['refresh_token']

    info.set_info_dict(info_dict)


def internal_spotify_call(method, endpoint):
    access_token = get_access_token()
    if not access_token:
        return 'blah'
    headers = {"Authorization": "Bearer {}".format(access_token)}

    index = request.url.find('?')
    get_parameters = '' if index == -1 else request.url[index:]
    url = spotify_url(endpoint) + get_parameters

    response = None

    if method == 'POST':
        response = requests.post(url, data=request.get_json(), headers=headers)
    elif method == 'GET':
        response = requests.get(url, data=request.get_json(), headers=headers)
    elif method == 'PUT':
        response = requests.put(url, data=request.get_json(), headers=headers)
    elif method == 'DELETE':
        response = requests.delete(url, data=request.get_json(), headers=headers)
    
    if response == None:
        app.logger.error('Invalid spotify request')
        return (None, 500)
    else:
        app.logger.debug('REQUEST: {} returned {}: {}'.format(url, response.status_code, response.content))
        return (response.get_json(), response.status_code)

def artist(artist_id):
    info, response_code = spotify.internal_spotify_call('GET', 'artists/{}'.format(artist_id))
    if not info or response_code != 200:
        app.logger.error('Failed to fetch artist: {}'.format(info))
        return False
    return spotify_object.artist_from_json(info)

# returns Array<Artist> if a valid artist
def related_artists(artist_id):
    info, response_code = spotify.internal_spotify_call('GET', 'artists/{}/related-artists'.format(artist_id))
    if not info or response_code != 200:
        app.logger.error('Failed to fetch artist: {}'.format(info))
        return False
    try:
        return [spotify_object.artist_from_json(artist) for artist in info['artists']]
    except Exception:
        app.logger.exception('Failed to parse artist: {}'.format(info))
        return False

# returns Array<Album> if a valid artist id
def top_albums_of_artist(artist_id):
    info, response_code = spotify.internal_spotify_call('GET', 'artists/{}/albums'.format(artist_id))
    if not info or response_code != 200:
        app.logger.error('Failed to fetch albums: {}'.format(info))
        return False
    try:
        return [spotify_object.album_from_json(album) for album in info['items']]
    except Exception:
        app.logger.exception('Failed to parse albums: {}'.format(info))
        return False

# returns: Array<Track> if valid artist id
def top_tracks_of_artist(artist_id):
    info, response_code = spotify.internal_spotify_call('GET', 'artists/{}/top-tracks'.format(artist_id))
    if not info or response_code != 200:
        app.logger.error('Failed to fetch tracks: {}'.format(info))
        return False
    try:
        return [spotify_object.track_from_json(album) for album in info['tracks']]
    except Exception:
        app.logger.exception('Failed to parse tracks: {}'.format(info))
        return False
