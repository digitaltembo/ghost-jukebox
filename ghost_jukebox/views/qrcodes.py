from flask import Flask, request, redirect, url_for, render_template
from ghost_jukebox import app, auth, common, conf
from ghost_jukebox.models import info, qr
from ghost_jukebox.views import spotify
from werkzeug.utils import secure_filename
import requests
import qrcode
from PIL import Image

from qrcode.main import make, QRCode
from qrcode.image.styledpil import *
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.constants import ERROR_CORRECT_Q
import os

# The images we generate are meant to fit on a standard CR-80 PVC ID Card
# Which has these dimensions in portrait
PATTERN_WIDTH = 638
PATTERN_HEIGHT = 1012


# Types:
SPOTIFY_TRACK    = 0
SPOTIFY_ALBUM    = 1
SPOTIFY_ARTIST   = 2
SPOTIFY_PLAYLIST = 3
ONLINE_RADIO     = 4

SPOTIFY_TYPES = [SPOTIFY_TRACK, SPOTIFY_ALBUM, SPOTIFY_ARTIST, SPOTIFY_PLAYLIST]

FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'

@app.route('/s//QR<code>')
def get_qr_info(code):
    qrinfo = qr.get_qr_info(code)
    if not qrinfo:
        return 'blah'

    if qrinfo.qrtype == SPOTIFY_TRACK:
        return redirect(url_for('track_info', track_id=qrinfo.uri))
    elif qrinfo.qrtype == SPOTIFY_ALBUM:
        return redirect(url_for('album_info', album_id=qrinfo.uri))
    elif qrinfo.qrtype == SPOTIFY_ARTIST:
        return redirect(url_for('artist_info', artist_id=qrinfo.uri))
    elif qrinfo.qrtype == SPOTIFY_PLAYLIST:
        return redirect(url_for('playlist_info', playlist_id=qrinfo.uri))

    elif qrinfo.qrtype == ONLINE_RADIO:
        radio_info_parts = qrinfo.uri.split('|')
        if len(radio_info_parts) != 2:
            return 'blah'
        return render_template(
            'qr_info_simple.html', 
            image_url = qrinfo.image_url, 
            title = radio_info_parts[0], 
            description = radio_info_parts[1]
        )

@app.route('/s//play/QR<code>')
def play_qr(code):
    return 'HAH!'

@app.route('/s//radio/QR<code>')
def generate_radio(code):
    return 'HAH'

@app.route('/s//QR/form-create')
def create_qr():
    return render_template(
        'qr_create.html'
    )

@app.route('/s//QR/create', methods=['GET'])
def make_qr():
    qrtype = request.form.get('qr_type')
    id     = request.form.get('qr_id')
    if not qrtpe or not id:
        return create_qr(errors='Fully specify the form!')

    code   = qr.get_next_code()
    qrdir    = qr_dir(code)
    os.mkdir(qrdir)
    image_url = request.form.get('image_url')
    app.logger.info("Making QR code from {}, {}, {}".format(qrtype, id, image_url))
    final_filename = False
    saved = common.download_image(image_url, qrdir)
    if not saved:
        return create_qr(errors='Fully specify the form!')
    cover_img = Image.open(os.join(qrdir, saved))

    qrinfo = qr.QRInfo(code, qrtype, id, saved)
    qr.insert(qrinfo)
    qr_image = get_qr_image(code)
    create_card_pattern(qr_image, cover_img, code, 'blah')
    retur redirect(url_for('view_qr', code=code))

@app.route('/s//QR<code>/view')
    return redirect(url_for('static', filename='qr_codes/qr{0:04d}/final.jpg'.format(code)))



def qr_dir(code):
    return "/home/pi/server/ghost_jukebox/static/qr_codes/qr{0:04d}".format(code)
"""
So: it turns out that the Raspberry Pi is pretty bad at the qr code generation
I pregenerated 1000 qr codes using this code:

    from qrcode.main import make, QRCode
    from qrcode.image.styledpil import *
    from qrcode.image.styles.colormasks import *
    from qrcode.image.styles.moduledrawers import *
    from qrcode.constants import ERROR_CORRECT_Q

    def make_code(code):
        qr = QRCode(error_correction=ERROR_CORRECT_Q)
        qr.add_data("https://jukebox.of.nolanhawk.in/s//QR{0:04d}".format(code))
        qr_image = qr.make_image(
            image_factory=StyledPilImage, 
            module_drawer=RoundedModuleDrawer(), 
            color_mask=RadialGradiantColorMask(center_color = PURPLE_RGBs, edge_color = (0,0,0)),
            image_path="/Users/nhawkins/Downloads/ghost2.png"
        )
        d = '../ghost-jukebox/ghost_jukebox/static/qr_codes/qr{0:04d}'.format(code)
        os.mkdir(d)
        qr_image.save("{}/qr_code.jpg".format(d))
        return qr_image


    for i in range(1, 1000):
        make_code()
"""
def get_qr_image(code):
    filename = qr_dir(code) + "/qr_code.png"

    qr_image.open(filename)
    return qr_image
 
def text_wrap(text, font, max_width):
    lines = []
    # If the width of the text is smaller than image width
    # we don't need to split it, just add it to the lines array
    # and return
    if font.getsize(text)[0] <= max_width:
        lines.append(text) 
    else:
        # split the line by spaces to get words
        words = text.split(' ')  
        i = 0
        # append every word to a line while its width is shorter than image width
        while i < len(words):
            line = '' 
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:                
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            # when the line gets longer than the max width do not append the word, 
            # add the line to the lines array
            lines.append(line)    
    return lines

def create_card_pattern(qr_code_img, cover_img, number, text):
    card = Image.new("RGB", (PATTERN_WIDTH * 2, PATTERN_HEIGHT), (255,255,255))

    cover_width, cover_height = cover_img.size
    cover = cover.resize((PATTERN_WIDTH, cover_height * PATTERN_WIDTH / cover_width), Image.LACZOS)
    cover_width, cover_height = cover_img.size
    front.paste(cover_img, (0, (PATTERN_HEIGHT - cover_height) / 2))

    qr_code_width, qr_code_height = qr_code_img.size 
    qr_code_img = qr_code_img.resize((PATTERN_WIDTH, qr_code_height * PATTERN_WIDTH / qr_code_width), Image.LACZOS)
    qr_code_width, qr_code_height = qr_code_img.size 
    qr_code_top = (PATTERN_HEIGHT - qr_code_height) / 2
    qr_code_bottom = (PATTERN_HEIGHT + qr_code_height) / 2
    back.paste(qr_code_img, (PATTERN_WIDTH, qr_code_top))
    backdraw = ImageDraw.Draw(back)


    font_file_path = '/home/pi/.fonts/Avenir-Medium.ttf'
    font = ImageFont.truetype(font_file_path, size=16, encoding="unic")

    backdraw.text((PATTERN_WIDTH + 30, qr_code_bottom + 30), "QR{}".format(number), font=font, fill=(0,0,0))
    offset = 30
    for line in text_wrap(text, font, PATTERN_WIDTH - 60):
        offset = offset + 15
        backdraw.text((PATTERN_WIDTH + 30, qr_code_bottom + offset), line, font=font, fill=(0,0,0))
    card.save(qr_dir(number) + "/final.jpg")









