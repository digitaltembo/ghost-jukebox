from flask import Flask, request, redirect, url_for, render_template
from ghost_jukebox import app, auth
from ghost_jukebox.models.db import info, qr

# Types:
SPOTIFY_TRACK    = 0
SPOTIFY_ALBUM    = 1
SPOTIFY_ARTIST   = 2
SPOTIFY_PLAYLIST = 3
ONLINE_RADIO     = 4

@app.route('/s//QR<code>')
def get_qr_info(code):
