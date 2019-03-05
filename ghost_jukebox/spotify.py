from flask import Flask, request, redirect, url_for, render_template
from io import BytesIO
from time import sleep
import datetime
import requests
from requests.auth import HTTPBasicAuth

from ghost_jukebox import app, auth, conf

class Token:
    def __self__(self):
        self.is_set = False 

    def set_token(self, access_token, refresh_token, expires_in):
        self.is_set = True
        self.access_token  = access_token
        self.refresh_token = refresh_token
        self.expiration    = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

    def get_token(self):
        # Can't set the tokens from here
        if not self.is_set:
            return False
        else:
            if datetime.datetime.now() < self.expiration:
                return access_token
            else:
                payload = {
                    'grant_type'   : 'refresh_token',
                    'refresh_token': self.refresh_token
                }

                token_response = requests.post(
                    spotify_url('accounts', 'api/token'),
                    data=payload,
                    auth=HTTPBasicAuth(conf.spotify_client, conf.spotify_secret)
                )
                try: 
                    j = token_response.json()
                    self.set_token(j['access_token'], j['refresh_token'], int(j['expires_in']))
                except:
                    self.set = False
                    return False
                return self.access_token

token = Token()

# just some fun scopes! These are the permissions granted by this authorization flow
scopes = [
    'user-modify-playback-state',
    'user-read-playback-state',
    'user-read-recently-played',
    'playlist-read-private',
    'user-read-currently-playing'
] 

def spotify_url(service, endpoint):
    if service == 'accounts':
        return 'https://{}.spotify.com/{}'.format(service, endpoint)
    else:
        return 'https://api.spotify.com/v1/{}/{}'.format(service, endpoint)


@app.route('/spotify/login')
@auth.login_required
def authorize():

    request_params = {
        'client_id'     : conf.spotify_client,
        'response_type' : 'code',
        'redirect_uri'  : 'https://{}{}'.format(conf.host, url_for('callback')),
        'scope'         : ' '.join(scopes)
    }

    url = requests.Request('GET', spotify_url('accounts', 'authorize'), params=request_params).prepare().url

    return redirect(url)

@app.route('/spotify/callback')
def callback():
    access_code = request.args.get('code','')
    if access_code:
        payload = {
            'grant_type'   : 'authorization_code',
            'code'         : access_code,
            'redirect_uri' : 'https://{}{}'.format(conf.host, url_for('callback'))
        }

        token_response = requests.post(
            spotify_url('accounts', 'api/token'),
            data=payload,
            auth=HTTPBasicAuth(conf.spotify_client, conf.spotify_secret)
        )
        try: 
            j = token_response.json()
            token.set_token(j['access_token'], j['refresh_token'], int(j['expires_in']))
            return 'AWESOME'
        except:
            return 'blah'
    else:
        error_code = request.args.get('error','Unknown Reason')
        return 'blah'

