from ghost_jukebox import app
import re
import requests

# get filename from content-disposition header
def get_filename_from_cd(cd):
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]

# This will download the image into the static folder
def download_image(image):
    response = requests.get(url, allow_redirects=True)
    filename = get_filename_from_cd(response.headers.get('content-disposition'))
    filename = filename if filename else url.split('/')[-1]
    destination_path = os.path.join(app.instance_path, 'static', 'imgs', filename)
    with open(destination_path, 'wb').write(response.content)