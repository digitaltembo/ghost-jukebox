from flask import Flask, request, redirect, url_for, render_template
from ghost_jukebox import app, auth, common, conf
from ghost_jukebox.models import info, qr
from ghost_jukebox.views import spotify
from werkzeug.utils import secure_filename
import requests
import qrcode
from PIL import Image, ImageDraw, ImageFont

from qrcode.main import make, QRCode
from qrcode.image.styledpil import *
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.constants import ERROR_CORRECT_Q
import os
import math

# The images we generate are meant to fit on a standard CR-80 PVC ID Card
# Which has these dimensions in portrait
PATTERN_WIDTH = 638
PATTERN_HEIGHT = 1012
CARD_WIDTH = PATTERN_WIDTH * 2
CARD_HEIGHT = PATTERN_HEIGHT

CARD_MARGIN = 300

PAPER_WIDTH = 85 * 30
PAPER_HEIGHT = 110 * 30



CARD_LOCATIONS = [
    ( int((PAPER_HEIGHT - CARD_MARGIN) / 2 - CARD_WIDTH), int((PAPER_WIDTH - CARD_MARGIN) / 2 - CARD_HEIGHT) ),
    ( int((PAPER_HEIGHT + CARD_MARGIN) / 2),              int((PAPER_WIDTH - CARD_MARGIN) / 2 - CARD_HEIGHT) ),
    ( int((PAPER_HEIGHT - CARD_MARGIN) / 2 - CARD_WIDTH), int((PAPER_WIDTH + CARD_MARGIN) / 2)               ),
    ( int((PAPER_HEIGHT + CARD_MARGIN) / 2),              int((PAPER_WIDTH + CARD_MARGIN) / 2)               )
]


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
def create_qr(errors=[]):
    return render_template(
        'qr_create.html'
    )

@app.route('/s//QR/create', methods=['GET'])
def make_qr():
    app.logger.info('Making the QR')
    qrtype = request.args.get('qr_type')
    id     = request.args.get('qr_id')
    text   = request.args.get('text')
    if not qrtype or not id or not text:
        return create_qr(errors='Fully specify the form!')

    code_str = qr.get_next_code()
    qrdir    = qr_dir(code_str)
    image_url = request.args.get('image_url')
    app.logger.info("Making QR code from {}, {}, {}".format(qrtype, id, image_url))
    final_filename = False
    saved = common.download_image(image_url, qrdir)
    if not saved:
        return create_qr(errors='Fully specify the form!')
    cover_img = Image.open(os.path.join(qrdir, saved))

    qrinfo = qr.QRInfo(code_str, qrtype, id, text)
    qr.insert(qrinfo)
    qr_image = get_qr_image(code_str)
    create_card_pattern(qr_image, cover_img, code_str, text)
    return redirect(url_for('view_qr', code_str=code_str))

@app.route('/s//QR<code_str>/view')
def view_qr(code_str):
    return render_template(
        'qr_view.html',
        image_path=url_for('static', filename='qr_codes/qr{}/final.jpg'.format(code_str))
    )


def split_list(liszt, max_size):
    return [
        liszt[i*max_size : i*max_size + max_size] 
        for i in range(int(math.ceil(float(len(liszt))/max_size)))
    ]

@app.route('/s//QRCards.pdf')
def view_all_qrs():
    largest = qr.get_largest_code()

    first = request.args.get('first')
    try:
        first = min(max(int(first),1), largest - 1)
    except:
        first = 1
    last  = request.args.get('last')
    try:
        last = max(min(int(last), largest), 1)
    except:
        last = largest 
    app.logger.info('Making PDF of {}-{} when the largest QR Codes is {}'.format(first, last, largest))
    infos = qr.get_all_sorted(first, last)

    CARDS_PER_PAGE = 4
    pages = split_list(list([info.code for info in infos]), CARDS_PER_PAGE)
    static_file = 'QRCards{}-{}.pdf'.format(first, last)
    file = '/home/pi/server/ghost_jukebox/static/{}'.format(static_file)
    for i, page in enumerate(pages):
        make_pdf_page(file, page, i == 0)

    return redirect(url_for('static', filename=static_file))


def make_pdf_page(file, page, first):
    image_paths = ['{}/final.jpg'.format(qr_dir(code_str)) for code_str in page]
    images = [Image.open(path) for path in image_paths]

    pdf_page = Image.new("RGB", (PAPER_HEIGHT, PAPER_WIDTH), (255,255,255))
    for i in range(len(images)):
        pdf_page.paste(images[i], CARD_LOCATIONS[i])

    pdf_page = pdf_page.transpose(Image.ROTATE_90)

    pdf_page.save(
        file,
        resolution=300,
        title='QR Cards',
        author='The Ghost',
        append=not first
    )

def qr_dir(code_str=None, code=None):
    if code:
        code_str = '{0:04d}'.format(code)
    return "/home/pi/server/ghost_jukebox/static/qr_codes/qr{}".format(code_str)
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
def get_qr_image(code_str):
    filename = qr_dir(code_str) + "/qr_code.jpg"

    qr_image = Image.open(filename)
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

def create_card_pattern(qr_code_img, cover_img, code_str, text):
    card = Image.new("RGB", (PATTERN_WIDTH * 2, PATTERN_HEIGHT), (255,255,255))

    cover_width, cover_height = cover_img.size
    cover_img = cover_img.resize((PATTERN_WIDTH, int(cover_height * PATTERN_WIDTH / cover_width)), Image.LANCZOS)
    cover_width, cover_height = cover_img.size
    card.paste(cover_img, (0, int((PATTERN_HEIGHT - cover_height) / 2)))

    qr_code_width, qr_code_height = qr_code_img.size 
    qr_code_img = qr_code_img.resize((PATTERN_WIDTH, int(qr_code_height * PATTERN_WIDTH / qr_code_width)), Image.LANCZOS)
    qr_code_width, qr_code_height = qr_code_img.size 
    qr_code_top = int((PATTERN_HEIGHT - qr_code_height) / 2)
    qr_code_bottom = int((PATTERN_HEIGHT + qr_code_height) / 2)
    card.paste(qr_code_img, (PATTERN_WIDTH, qr_code_top))
    carddraw = ImageDraw.Draw(card)

    carddraw.rectangle((0,0,PATTERN_WIDTH - 1, PATTERN_HEIGHT - 1), outline=(127,127,127))
    carddraw.rectangle((PATTERN_WIDTH,0,PATTERN_WIDTH*2 - 1, PATTERN_HEIGHT - 1), outline=(127,127,127))


    # Draw the text "QR####" on top of the qr code
    text_box(
        'QR{}'.format(code_str), 
        carddraw, 
        ImageFont.truetype(FONT_PATH, size=16, encoding="unic"),
        (PATTERN_WIDTH + 60, qr_code_top, PATTERN_WIDTH - 120, 20),
        horizontal_allignment = ALLIGNMENT_CENTER,
        vertical_allignment = ALLIGNMENT_BOTTOM,
        fill=(0,0,0)
    )
    # Draw the text for the given card under the qr code
    text_box(
        text, 
        carddraw, 
        ImageFont.truetype(FONT_PATH, size=32, encoding="unic"),
        (PATTERN_WIDTH + 60, qr_code_bottom, PATTERN_WIDTH - 120, 20),
        horizontal_allignment = ALLIGNMENT_CENTER,
        vertical_allignment = ALLIGNMENT_TOP,
        fill=(0,0,0)
    )
    card.save(qr_dir(code_str) + "/final.jpg")


def font(font_path, size):
    return ImageFont.truetype(font_path, size=size, encoding="unic")

ALLIGNMENT_LEFT = 0
ALLIGNMENT_CENTER = 1
ALLIGNMENT_RIGHT = 2
ALLIGNMENT_TOP = 3
ALLIGNMENT_BOTTOM = 4
def text_box(text, image_draw, font, box, horizontal_allignment = ALLIGNMENT_LEFT, vertical_allignment = ALLIGNMENT_TOP, **kwargs):
    x = box[0]
    y = box[1]
    width = box[2]
    height = box[3]
    lines = text.split('\n')
    true_lines = []
    for line in lines:
        if font.getsize(line)[0] <= width:
            true_lines.append(line) 
        else:
            current_line = ''
            for word in line.split(' '):
                if font.getsize(current_line + word)[0] <= width:
                    current_line += ' ' + word 
                else:
                    true_lines.append(current_line)
                    current_line = word 
            true_lines.append(current_line)
    
    x_offset = y_offset = 0
    lineheight = font.getsize(true_lines[0])[1] * 1.2 # Give a margin of 0.2x the font height
    if vertical_allignment == ALLIGNMENT_CENTER:
        y_offset = - (len(true_lines) * lineheight) / 2
    elif vertical_allignment == ALLIGNMENT_BOTTOM:
        y_offset = - (len(true_lines) * lineheight)
    
    for line in true_lines:
        linewidth = font.getsize(line)[0]
        if horizontal_allignment == ALLIGNMENT_CENTER:
            x_offset = (width - linewidth) / 2
        elif horizontal_allignment == ALLIGNMENT_RIGHT:
            x_offset = width - linewidth
        image_draw.text(
            (int(x + x_offset), int(y + y_offset)),
            line,
            font=font,
            **kwargs
        )
        y_offset += lineheight




