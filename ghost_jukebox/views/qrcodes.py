from flask import Flask, request, redirect, url_for, render_template
from ghost_jukebox import app, auth
from ghost_jukebox.models import info, qr
from ghost_jukebox.views import spotify

@app.route('/s//QR<code>')
def get_qr_info(code):
    qrinfo = qr.get_qr_info(code)
    if not qrinfo:
        return 'blah'

    if qrinfo.qrtype == qr.SPOTIFY_TRACK:
        return redirect(url_for('track_info', track_id=qrinfo.uri))
    elif qrinfo.qrtype == qr.SPOTIFY_ALBUM:
        return redirect(url_for('album_info', album_id=qrinfo.uri))
    elif qrinfo.qrtype == qr.SPOTIFY_ARTIST:
        return redirect(url_for('artist_info', artist_id=qrinfo.uri))
    elif qrinfo.qrtype == qr.SPOTIFY_PLAYLIST:
        return redirect(url_for('playlist_info', playlist_id=qrinfo.uri))

    elif qrinfo.qrtype == qr.ONLINE_RADIO:
        radio_info_parts = qrinfo.uri.split('|')
        if len(radio_info_parts) != 2:
            return 'blah'
        return render_template(
            'qr_info_simple.html', 
            image_url = qrinfo.image_url, 
            title = radio_info_parts[0], 
            description = radio_info_parts[1]
        )

@app.route('/s//play/QR<code>')
def play_qr(code):
    return 'HAH!'

@app.route('/s//radio/QR<code>')
def generate_radio(code):
    return 'HAH'



