from flask import Flask, request, redirect, url_for, render_template
from ghost_jukebox import app, auth
from ghost_jukebox.models.db import info, qr

@app.route('/s//QR<code>')
def get_qr_info(code):
    qrinfo = qr.get_qr_info(code)
    if not qrinfo:
        return 'blah'

    if qrinfo.type == qr.SPOTIFY_TRACK:
        return render_spotify_track(qrinfo)
    elif qrinfo.type == qr.SPOTIFY_ALBUM:
        return render_spotify_album(qrinfo)
    elif qrinfo.type == qr.SPOTIFY_ARTIST:
        return render_spotify_artist(qrinfo)
    elif qrinfo.type == qr.SPOTIFY_PLAYLIST:
        return render_spotify_playlist(qrinfo)
    elif qrinfo.type == qr.ONLINE_RADIO:
        radio_info_parts = qrinfo.uri.split('|')
        if len(radio_info_parts) != 2:
            return 'blah'
        return render_template(
            'qr_info_simple.html', 
            image_url = qrinfo.image_url, 
            title = radio_info_parts[0], 
            description = radio_info_parts[1]
        )

def render_spotify_artist(qrinfo):
    artist_id = qrinfo.uri
    artist = spotify.artist(artist_id)
    if not artist:
        return 'dang'
    related_artists = spotify.related_artists(artist_id)
    top_tracks = spotify.top_tracks_of_artist(artist_id)
    top_albums = spotify.top_albums(artist_id)
    return render_template(
        'qr_info_artist.html',
        image_url = qrinfo.image_url, 
        title = artist.name,
        albums = top_albums,
        related_artists = related_artists,
        tracks = top_tracks 
    )





SPOTIFY_ALBUM
SPOTIFY_ARTIST
SPOTIFY_PLAYLIST
ONLINE_RADIO
