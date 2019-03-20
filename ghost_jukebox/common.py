from ghost_jukebox import app

import os
import random
import re
import requests
import string

from werkzeug.utils import secure_filename


# get filename from content-disposition header
def get_filename_from_cd(cd):
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]

# This will download the image into the static folder
def download_image(image_url, path, filename = None):
    response = requests.get(image_url, allow_redirects=True)
    if not filename:
        filename = get_filename_from_cd(response.headers.get('content-disposition'))
        filename = filename if filename else image_url.split('/')[-1]
    destination_path = os.path.join(path, filename)
    with open(destination_path, 'wb') as file:
        file.write(response.content)
    return filename

def save_file(request, name, path):
    app.logger.info('Checking the request for the file: {}'.format(request.files))
    app.logger.info(str(request))
    if name not in request.files:
        app.logger.info('Name not in file :(')
        return False
    file = request.files[name]
    if not file or file.filename == '':
        app.logger.info('{} and {}'.format(file, file.filename))
        return False
    filename = secure_filename(file.filename)
    file.save(os.path.join(path, filename))
    return filename

def random_string(length=10):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))
