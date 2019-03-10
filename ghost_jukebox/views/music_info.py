from flask import Flask, request, redirect, url_for, render_template
from ghost_jukebox import app, auth
from ghost_jukebox.views import spotify

def get_image(image_set):
    if image_set:
        try:
            return image_set.get_by_size(target_width=640).url
        except Exception:
            app.logger.exception('Dang!')
    return ''

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
        image_url = get_image(artist.image_set),
        title = artist.name,
        albums = top_albums,
        related_artists = related_artists,
        tracks = top_tracks 
    )
    

@app.route('/s//info/album/<album_id>')
def album_info(album_id):
    album = spotify.album(album_id)
    if not album:
        return 'dang'

    return render_template(
        'album_info.html',
        image_url = get_image(album.image_set), 
        album = album
    )

@app.route('/s//info/track/<track_id>')
def track_info(track_id):
    track = spotify.track(track_id)
    if not track:
        return 'dang'

    return render_template(
        'track_info.html',
        track = track
    )

@app.route('/s//info/playlist/<playlist_id>')
def playlist_info(playlist_id):
    playlist = spotify.playlist(playlist_id)
    if not playlist:
        return 'dang'

    return render_template(
        'playlist_info.html',
        image_url = get_image(playlist.image_set),
        playlist = playlist
    )

@app.route('/s//info/user/<user_id>')
def user_info(user_id):
    user = spotify.user(user_id)
    if not user:
        return 'dang'

    return render_template(
        'user_info.html',
        image_url = get_image(user.image_set),
        user = user
    )
