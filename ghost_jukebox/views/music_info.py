from flask import Flask, request, redirect, url_for, render_template
from ghost_jukebox import app, auth
from ghost_jukebox.views import spotify


@app.route('/s//info/artist/<artist_id>')
def artist_info(artist_id):
    artist = spotify.artist(artist_id)
    if not artist:
        return 'dang'
    related_artists = spotify.related_artists(artist_id)
    top_tracks = spotify.top_tracks_of_artist(artist_id)
    top_albums = spotify.top_albums_of_artist(artist_id)
    return render_template(
        'artist_info.html',
        image_url = artist.image_set.get_by_size(width=640).url, 
        title = artist.name,
        albums = top_albums,
        related_artists = related_artists,
        tracks = top_tracks 
    )
    

@app.route('/s//info/album/<album_id>')
def album_info(album_id):
    album = spotify.album(album_id)
    if not artist:
        return 'dang'

    return render_template(
        'album_info.html',
        image_url = album.image_set.get_by_size(width=640).url, 
        album = album
    )

@app.route('/s//info/track/<track_id>')
def track_info(track_id):
    track = spotify.track(track)
    if not track:
        return 'dang'

    return render_template(
        'track_info.html',
        track = track
    )

@app.route('/s//info/playlist/<playlist_id>')
def playlist_info(playlist_id):
    playlist = spotify.playlist(playlist)
    if not playlist:
        return 'dang'

    return render_template(
        'playlist_info.html',
        image_url = playlist.image_set.get_by_size(width=640).url, 
        playlist = playlist
    )