from flask import Flask, request, redirect, url_for, render_template
from io import BytesIO
from time import sleep
from PIL import Image
import time

from ghost_jukebox import app, auth

@app.rout('/')
@auth.login_required
def root():
    return redirect(url_for('home'))

