from ghost_jukebox import app 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8443, ssl_context='adhoc')
