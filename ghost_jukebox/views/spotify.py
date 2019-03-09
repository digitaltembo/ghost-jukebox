from flask import Flask, request, redirect, url_for, render_template
from io import BytesIO
from time import sleep
import datetime
import requests
from requests.auth import HTTPBasicAuth

from ghost_jukebox import app, auth, conf
import ghost_jukebox.models.info 

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
    return (datetime.datetime.now() + datetime.timedelta(seconds=expires_in)).timestamp()


@app.route('/spotify/login')
@auth.login_required
def authorize():

    request_params = {
        'client_id'     : conf.spotify_client,
        'response_type' : 'code',
        'redirect_uri'  : 'https://{}{}'.format(conf.host, url_for('callback')),
        'scope'         : ' '.join(scopes)
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
            spotify_url('accounts', 'api/token'),
            data=payload,
            auth=HTTPBasicAuth(conf.spotify_client, conf.spotify_secret)
        )
        token_info = {}
        try: 
            j = token_response.json()
            token_info = 
        except:
            return 'blah'
        try:
            info.set_info_dict(token_info)
            return 'COOOL'
        except:
            return 'blah'
    else:
        error_code = request.args.get('error','Unknown Reason')
        return 'blah'

@app.route('/spotify/api/<method>/<path:endpoint>')
@auth.login_required
def forwardSpotifyApiCall(method, endpoint):
    access_token = get_access_token()
    if not access_token:
        return 'blah'
    headers = {"Authorization": "Bearer {}".format(access_token)}
    url = spotify_url(endpoint)
    response = None

    if method == 'POST':
        response = requests.post(url, data=request.get_json(), headers=headers)
    elif method == 'GET':
        response = requests.get(url, data=request.get_json(), headers=headers)
    elif method == 'PUT':
        response = requests.put(url, data=request.get_json(), headers=headers)

    elif method == 'DELETE':
        response = requests.delete(url, data=request.get_json(), headers=headers)

    if response = None:
        return 'blah'
    return (resp.content, resp.status_code, resp.headers.items())

def get_access_token():
    access_token  = get_info(info.SPOTIFY_ACCESS_TOKEN)
    refresh_token = get_info(info.SPOTIFY_REFRESH_TOKEN)
    expiration    = datetime.fromtimestamp(float(get_info(info.SPOTIFY_TOKEN_EXPIRATION)))
    if not access_token:
        return False 
    else:
        if datettime.now() < expiration:
            return access_token
        else:
            payload = {
                'grant_type'   : 'refresh_token',
                'refresh_token': self.refresh_token
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
    info.set_info_dict({
        info.SPOTIFY_ACCESS_TOKEN:     j['access_token']
        info.SPOTIFY_REFRESH_TOKEN:    j['refresh_token']
        info.SPOTIFY_TOKEN_EXPIRATION: get_expiration_time(j['expires_in'])
    }


