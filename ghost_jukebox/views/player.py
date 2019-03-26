from flask import Flask, request, redirect, url_for, render_template
from io import BytesIO
from time import sleep
from PIL import Image
import time

from ghost_jukebox import app, basic_auth

DEVICE_ID = 'DEVICE_ID'

@app.route('/s//play/<music_type>/<item_id>')
@home_auth
def play(music_type, item_id):
    if music_type == 'track':
        play_track(item_id)
    elif music_type == 'album':
        play_album(item_id)
    elif music_type == 'artist':
        play_artist(item_id)
    elif music_type == 'playlist':
        play_playlist(item_id)
    elif music_type == 'radio':
        play_radio(item_id)
    else:
        return 'blah'

@app.route('/s//enqueue/<music_type>/<item_id>')
@home_auth
def enqueue(music_type, item_id):
    queue.enqueue('{}/{}'.format(music_type, item_id))
    return ':)'

@app.route('/s//shuffle/<music_type>/<item_id>')
@home_auth
def shuffle(music_type, item_id):
    if music_type == 'track':
        play_track(item_id)
    elif music_type == 'album':
        shuffle_album(item_id)
    elif music_type == 'artist':
        shuffle_artist(item_id)
    elif music_type == 'playlist':
        shuffle_playlist(item_id)
    elif music_type == 'radio':
        play_radio(item_id)
    else:
        return 'blah'

@app.route('/s//radio/<music_type>/<item_id>')
@home_auth
def radio(music_type, item_id):
    if music_type == 'track':
        track_radio(item_id)
    elif music_type == 'album':
        album_radio(item_id)
    elif music_type == 'artist':
        artist_radio(item_id)
    elif music_type == 'playlist':
        playlist_radio(item_id)
    elif music_type == 'radio':
        play_radio(item_id)
    else:
        return 'blah'


# called by the QR reader alone, when it thinks it should stop playing the current thing
@app.route('/s//QRstop')
@home_auth
def stop_qr(item_id):
    next_item = queue.pop()
    if next_item:
        return redirect('/s//play/{}'.format(next_item))
    else:
        pause()


@app.route('/s//play/')
@home_auth
def resume():
    # figure out whats playing?
    return 'hmm'

@app.route('/s//pause/')
@home_auth
def pause():
    # stop whats playing?
    return 'hmm'

def get_device_id():
    return 
def play_track(track_id):
    device_id = info.get_info(DEVICE_ID)
    if device_id:
        result, response_code = spotify.play_tracks(device_id, ["spotify:track:{}".format(track_id)])
    return 'hmmm'

def play_album(album_id):
    device_id = info.get_info(DEVICE_ID)
    if device_id:
        result, response_code = spotify.play(device_id, "spotify:album:{}".format(album_id))
        return 'hmmm'
    else:
        return 'blah :(' #redirect(url_for('setup')) ? 

def play_artist(artist_id):
    device_id = info.get_info(DEVICE_ID)
    if device_id:
        result, response_code = spotify.play(device_id, "spotify:artist:{}".format(artist_id))
        return 'hmmm'
    else:
        return 'blah :(' #redirect(url_for('setup')) ? 

def play_playlist(playlist_id):
    device_id = info.get_info(DEVICE_ID)
    if device_id:
        result, response_code = spotify.play(device_id, "spotify:playlist:{}".format(playlist_id))
        return 'hmmm'
    else:
        return 'blah :(' #redirect(url_for('setup')) ? 

def play_radio(radio_id):
    device_id = info.get_info(DEVICE_ID)
    if device_id:
        result, response_code = spotify.play(device_id, "spotify:playlist:{}".format(playlist_id))
        return 'hmmm'
    else:
        return 'blah :(' #redirect(url_for('setup')) ? 



