from flask import Flask, request, redirect, url_for
from io import BytesIO
from time import sleep
from picamera import PiCamera
from PIL import Image
import time

from ghost_jukebox import app, auth

# initialize the camera
camera = PiCamera()
camera.resolution = (1024, 768)

@app.route('/')
@auth.login_required
def hello_world():
    return 'Hello, {}!'.format(auth.username())

@app.route('/capture')
@auth.login_required
def capture():
    filename = '{}.jpg'.format(time.time())
    camera.capture('ghost_jukebox/static/pics/{}'.format(filename))
    url = url_for('static', filename='pics/{}'.format(filename))
    return redirect(url)

