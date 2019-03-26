from flask import Flask

from ghost_jukebox import conf, security

# initialize Flask app
app = Flask(__name__)
# Initialize Authorization
basic_auth = security.basic_auth

home_auth = security.home_auth


# Just going to do a one user system for now, with username and password configured in environment variables
users = {conf.username: conf.password}

app.config['UPLOAD_FOLDER'] = conf.upload_folder

import ghost_jukebox.views.home
import ghost_jukebox.views.cards
import ghost_jukebox.views.music_info
import ghost_jukebox.views.player
import ghost_jukebox.views.spotify
