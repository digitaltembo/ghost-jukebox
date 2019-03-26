from flask import Flask, request, redirect, url_for, render_template
from io import BytesIO
from time import sleep
from PIL import Image
import time

from ghost_jukebox import app, basic_auth

@app.route('/')
@basic_auth.login_required
def root():
    return redirect(url_for('home'))

# all of the traffic
@app.route('/s')
@basic_auth.login_required
def home():
    return render_template('index.html', name=auth.username())



