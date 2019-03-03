from flask import Flask, request, send_from_directory
from flask_httpauth import HTTPBasicAuth
from io import BytesIO
from time import sleep
from picamera import PiCamera
from PIL import Image
import time
import os

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {}

def setup_users():
    if 'GHOST_JUKEBOX_UNAME' in os.environ:
        users[os.environ['GHOST_JUKEBOX_UNAME']] = os.environ['GHOST_JUKEBOX_PSWD']
    else:
        users['admin'] = 'password'

setup_users()

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


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
        return None

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8443, ssl_context='adhoc')

