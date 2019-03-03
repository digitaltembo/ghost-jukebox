from flask import Flask, request, send_from_directory
from io import BytesIO
from time import sleep
from picamera import PiCamera
from PIL import Image
import time

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
    camera.capture('imgs/{}'.format(filename))
    return send_from_directory('imgs', filename)
