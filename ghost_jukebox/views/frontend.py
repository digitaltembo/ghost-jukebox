from flask import Flask, request, redirect, url_for, render_template
from ghost_jukebox import app, auth

# all of the traffic
@app.route('/s')
@auth.login_required
def home():
    return render_template('index.html', name=auth.username())