from flask import Flask, request, redirect, url_for, render_template
from io import BytesIO
from time import sleep
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote

from ghost_jukebox import app, auth, conf
from ghost_jukebox.models import info 
from ghost_jukebox.views import spotify_objects

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


def internal_spotify_call(method, endpoint, params={}):
    access_token = get_access_token()
    if not access_token:
        return 'blah'
    headers = {"Authorization": "Bearer {}".format(access_token)}

    url = spotify_url(endpoint)

    response = None

    if method == 'POST':
        response = requests.post(url, params=params, headers=headers)
    elif method == 'GET':
        response = requests.get(url, params=params, headers=headers)
    elif method == 'PUT':
        response = requests.put(url, params=params, headers=headers)
    elif method == 'DELETE':
        response = requests.delete(url, params=params, headers=headers)
    
    if response == None:
        app.logger.error('Invalid spotify request')
        return (None, 500)
    else:
        app.logger.debug('REQUEST: {} returned {}: {}'.format(url, response.status_code, response.content))
        return (response.json(), response.status_code)

# returns Artist
def artist(artist_id):
    info, response_code = internal_spotify_call('GET', 'artists/{}'.format(artist_id))
    if not info or response_code != 200:
        app.logger.error('Failed to fetch artist: {}'.format(info))
        return False
    return spotify_objects.artist_from_json(info)


# returns Array<Artist> if a valid artist
def related_artists(artist_id):
    info, response_code = internal_spotify_call('GET', 'artists/{}/related-artists'.format(artist_id))
    if not info or response_code != 200:
        app.logger.error('Failed to fetch artist: {}'.format(info))
        return False
    return [spotify_objects.artist_from_json(artist) for artist in info['artists']]

# returns Array<Album> if a valid artist id
def top_albums_of_artist(artist_id):
    info, response_code = internal_spotify_call('GET', 'artists/{}/albums'.format(artist_id))
    if not info or response_code != 200:
        app.logger.error('Failed to fetch albums: {}'.format(info))
        return False
    return [spotify_objects.album_from_json(album) for album in info['items']]

# returns: Array<Track> if valid artist id
def top_tracks_of_artist(artist_id):
    info, response_code = internal_spotify_call('GET', 'artists/{}/top-tracks?country=us'.format(artist_id))
    if not info or response_code != 200:
        app.logger.error('Failed to fetch tracks: {}'.format(info))
        return False
    return [spotify_objects.track_from_json(album) for album in info['tracks']]

# returns: Album
def album(album_id):
    info, response_code = internal_spotify_call('GET', 'albums/{}'.format(album_id))
    if not info or response_code != 200:
        app.logger.error('Failed to fetch album: {}'.format(info))
        return False
    return spotify_objects.album_from_json(info)

# returns: Track
def track(track_id):
    info, response_code = internal_spotify_call('GET', 'tracks/{}'.format(track_id))
    if not info or response_code != 200:
        app.logger.error('Failed to fetch track: {}'.format(info))
        return False
    return spotify_objects.track_from_json(info)

# returns: Playlist
def playlist(playlist_id):
    info, response_code = internal_spotify_call('GET', 'playlists/{}'.format(playlist_id))
    if not info or response_code != 200:
        app.logger.error('Failed to fetch playlist: {}'.format(info))
        return False
    return spotify_objects.playlist_from_json(info)

def user(user_id):
    info, response_code = internal_spotify_call('GET', 'users/{}'.format(user_id))
    if not info or response_code != 200:
        app.logger.error('Failed to fetch user: {}'.format(info))
        return False
    return spotify_objects.user_from_json(info)

# returns: Array<Playlist>
def users_playlists(user_id):
    info, response_code = internal_spotify_call('GET', 'users/{user_id}/playlists'.format(user_id))
    if not info or response_code != 200:
        app.logger.error('Failed to fetch playlists: {}'.format(info))
        return False
    return [spotify_objects.playlist_from_json(playlist) for playlist in info['items']]

# returns: User
def populate_users_playlists(user):
    user.playlists = users_playlists(user.id)
    return user

SEARCH_ALBUM    = 'album'
SEARCH_ARTIST   = 'artist'
SEARCH_PLAYLIST = 'playlist'
SEARCH_TRACK    = 'track'
ALL_SEARCHES = [SEARCH_ALBUM, SEARCH_ARTIST, SEARCH_PLAYLIST, SEARCH_TRACK]
# returns: SearchResults
def search(search, search_types = ALL_SEARCHES):
    params = {
        'q': search,
        'type': ','.join(filter(lambda search_type: search_type in ALL_SEARCHES, search_types))
    }
    info, response_code = internal_spotify_call('GET', 'search', params=params)
    if not info or response_code != 200:
        app.logger.error('Failed to search: {}'.format(search))
        return False
    return spotify_objects.search_results_from_json(info)


