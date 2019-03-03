from flask import Flask
from flask_httpauth import HTTPBasicAuth
import os

# initialize Flask app
app = Flask(__name__)
# INitialize Authorization
auth = HTTPBasicAuth()


# Just going to do a one user system for now, with username and password configured in environment variables
users = {}
def setup_users():
    if 'GHOST_JUKEBOX_UNAME' in os.environ:
        users[os.environ['GHOST_JUKEBOX_UNAME']] = os.environ['GHOST_JUKEBOX_PSWD']
    else:
        users['admin'] = 'password'
setup_users()

# I am ok with this as a super insecure authentication method so long as I am the only user
@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
        return None

import ghost_jukebox.views

