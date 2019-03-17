from ghost_jukebox import app
import re
import requests
import os

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
        filename = filename if filename else url.split('/')[-1]
    destination_path = os.path.join(path, filename)
    with open(destination_path, 'wb') as file:
        file.write(response.content)
    return filename

def save_file(request, name, path):
    if name not in request.files:
        return False
    file = request.files[name]
    if not file or file.filename == '':
        return False
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.instance_path, 'static', path, filename))
    return filename

PURPLE_RGBs = (96,0,152)