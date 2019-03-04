from flask import Flask, request, redirect, url_for, render_template
from io import BytesIO
from time import sleep
from picamera import PiCamera
from PIL import Image
import time

from ghost_jukebox import app, auth

# initialize the camera
camera = PiCamera()
camera.resolution = (1024, 768)

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

@app.route('/')
@auth.login_required
def hello_world():
    return render_template('index.html', name=auth.username())

@app.route('/capture')
@auth.login_required
def capture():
    filename = '{}.jpg'.format(time.time())
    camera.capture('ghost_jukebox/static/pics/{}'.format(filename))
    url = url_for('static', filename='pics/{}'.format(filename))
    return redirect(url)

