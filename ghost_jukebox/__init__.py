from flask import Flask
from flask_httpauth import HTTPBasicAuth

from ghost_jukebox import conf

# initialize Flask app
app = Flask(__name__)
# INitialize Authorization
auth = HTTPBasicAuth()


# Just going to do a one user system for now, with username and password configured in environment variables
users = {conf.username: conf.password}

# I am ok with this as a super insecure authentication method so long as I am the only user
@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
        return None

import ghost_jukebox.views
import ghost_jukebox.spotify
