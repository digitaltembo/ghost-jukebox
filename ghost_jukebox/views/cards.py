from flask import Flask, request, redirect, url_for, render_template

from ghost_jukebox import app, auth, common, conf
from ghost_jukebox.models import info, card

import math
import os

from PIL import Image, ImageDraw, ImageFont

"""
Cards

Cards are the backbone of the Ghost Jukebox. They are the analog of Records, CDs, and Tapes
Cards are PVC ID Cards, probably, that have a cover image on one side and a QR Code on the back.
A Card, much like a Record, CD, or Tape, contains the essence of Music. In this case, the QR Code 
references an index in the <card> table, which in turn references something playable from Spotify
(a track, album, artist, or playlist) or an online radio station.
Specifically, the QR Code is a link in the pattern of https://<host>/s//QR#### (I hope I don't 
get more than 9999 of these). The link is meant to be read by the Ghost Jukebox itself, but will 
also just bring up the info page on the referenced music item if scanned by a usual QR Code Reader.

This view handles the creation and editing of cards, as well as handling calls that might be gotten
from a scan of the QR code on the back of the card.
"""

# Types (Maybe I'll add to these!)
SPOTIFY_TRACK    = 0
SPOTIFY_ALBUM    = 1
SPOTIFY_ARTIST   = 2
SPOTIFY_PLAYLIST = 3
ONLINE_RADIO     = 4

SPOTIFY_TYPES = [SPOTIFY_TRACK, SPOTIFY_ALBUM, SPOTIFY_ARTIST, SPOTIFY_PLAYLIST]

TYPE_NAMES = {
    SPOTIFY_TRACK: 'track',
    SPOTIFY_ALBUM: 'album',
    SPOTIFY_ARTIST: 'artist',
    SPOTIFY_PLAYLIST: 'playlist',
    ONLINE_RADIO:'radio'
}

FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'


# The images we generate are meant to fit on a standard CR-80 PVC ID Card
# Which has these dimensions in portrait
CARD_WIDTH = 638
CARD_HEIGHT = 1012
PATTERN_WIDTH = CARD_WIDTH * 2 # I write on _both_ sides of the ID Card
PATTERN_HEIGHT = CARD_HEIGHT

PATTERN_MARGIN = 300 # Put this margin in between patterns on the paper

PAPER_WIDTH = 85 * 30
PAPER_HEIGHT = 110 * 30

# These are the locations of the cards spread over the paper. Each sheet of 8.5 x 11 paper can hold only 4 cards, front and back
PATTERN_LOCATIONS = [
    ( int((PAPER_HEIGHT - PATTERN_MARGIN)/2 - PATTERN_WIDTH), int((PAPER_WIDTH - PATTERN_MARGIN)/2 - PATTERN_HEIGHT) ),
    ( int((PAPER_HEIGHT + PATTERN_MARGIN)/2),                 int((PAPER_WIDTH - PATTERN_MARGIN)/2 - PATTERN_HEIGHT) ),
    ( int((PAPER_HEIGHT - PATTERN_MARGIN)/2 - PATTERN_WIDTH), int((PAPER_WIDTH + PATTERN_MARGIN)/2)               ),
    ( int((PAPER_HEIGHT + PATTERN_MARGIN)/2),                 int((PAPER_WIDTH + PATTERN_MARGIN)/2)               )
]

# Helper Funcs: the files pertinent to the individual cards are stored in a directory given by the code:
def static_dir(code=None, code_num=None):
    if code_num:
        code = card.strify(code_num)
    return "cards/qr{}".format(code)

def full_dir(code=None, code_num=None):
    return "/home/pi/server/ghost_jukebox/static/{}".format(static_dir(code, code_num))



@app.route('/s//QR<code>')
@auth.login_required
def get_qr_info(code):
    card_info = card.get_card_info(code)
    if not card_info:
        return 'blah'

    if card_info.card_type == SPOTIFY_TRACK:
        return redirect(url_for('track_info', track_id=card_info.item_id))
    elif card_info.card_type == SPOTIFY_ALBUM:
        return redirect(url_for('album_info', album_id=card_info.item_id))
    elif card_info.card_type == SPOTIFY_ARTIST:
        return redirect(url_for('artist_info', artist_id=card_info.item_id))
    elif card_info.card_type == SPOTIFY_PLAYLIST:
        return redirect(url_for('playlist_info', playlist_id=card_info.item_id))
    elif card_info.card_type == ONLINE_RADIO:
        # PENDING REDESIGN
        return 'blah'

@app.route('/s//play/QR<code>')
@auth.login_required
def play_qr(code):
    return 'HAH!'

@app.route('/s//radio/QR<code>')
@auth.login_required
def generate_radio(code):
    return 'HAH'


@app.route('/s//card/edit')
@auth.login_required
def edit_card_view():
    return edit_card(
        code      = request.args.get('code'),
        card_type = request.args.get('card_type'),
        item_id   = request.args.get('item_id'),
        text      = request.args.get('text')
    )

def edit_card(errors=[], code=None, card_type=None, item_id=None, text=None):
    if any([code, card_type, item_id, text]) and all([code, card_type, item_id, text]):
        return render_template(
            'card_edit.html',
            errors    = errors,
            editing   = True,
            code      = code,
            card_type = card_type,
            item_id   = item_id,
            text      = text,
            card_img  = url_for('static', filename="{}/final.jpg".format(static_dir(code))),
            cache_breaker = common.random_string(5)
        )
    return render_template(
        'card_edit.html',
        errors    = errors,
        editing   = False,
        code      = '',
        card_type = 0,
        item_id   = '',
        text      = '',
        cache_breaker = common.random_string(5)
    )

@app.route('/s//QR<code>/view')
@auth.login_required
def view_card(code):
    info = card.get_card_info(code)
    if info:
        return edit_card(
            code=code, 
            card_type=info.card_type, 
            item_id=info.item_id, 
            text=info.title
        )
    else:
        return edit_card()


# This does the heavy lifting of actually saving a given card
@app.route('/s//card/save', methods=['GET', 'POST'])
@auth.login_required
def save_card():
    if request.method == 'GET':
        card_type =     request.args.get('card_type')
        item_id   =     request.args.get('item_id')
        text      =     request.args.get('text')
        specific_code = request.args.get('code')
        image_url =     request.args.get('image_url')
    elif request.method == 'POST':
        card_type =     request.form.get('card_type')
        item_id   =     request.form.get('item_id')
        text      =     request.form.get('text')
        specific_code = request.form.get('code')
        image_url =     request.form.get('image_url')

    if not card_type or not item_id or not text:
        return edit_card(errors='Fully specify the form!')

    code    = specific_code if specific_code else card.get_next_code()
    carddir = full_dir(code)

    # try first to get an image upload
    app.logger.info(request.files)
    uploaded_file = common.save_file(request, 'image_upload', carddir)
    if not uploaded_file:
        # otherwise, see if the image url is specified
        if image_url:
            uploaded_file = common.download_image(image_url, carddir)
        if not uploaded_file:
            return edit_card(errors='Failed to download image. Is that the correct file?')

    cover_img = Image.open(os.path.join(carddir, uploaded_file))

    qr_image = get_qr_image(code)

    create_card_pattern(qr_image, cover_img, code, text)

    if specific_code:
        card.update(card.CardInfo(code, card_type, item_id, text))
    else:
        card.insert(card.CardInfo(code, card_type, item_id, text))

    return redirect(url_for('view_card', code=code))


"""
So: it turns out that the Raspberry Pi is pretty bad at the qr code generation (it takes foreeeevver)
I pregenerated 1000 qr codes using this code (will hopefully remember to do it again when I run out):

    from qrcode.main import make, QRCode
    from qrcode.image.styledpil import *
    from qrcode.image.styles.colormasks import *
    from qrcode.image.styles.moduledrawers import *
    from qrcode.constants import ERROR_CORRECT_Q

    def make_code(code):
        qr = QRCode(error_correction=ERROR_CORRECT_Q)
        qr.add_data("https://<HOST>/s//QR{0:04d}".format(code))
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

Oh, and! I wrote the code to allow QR Codes with Fancy Styles, that is in another of my repos and in a PR
to python-qrcode

"""
def get_qr_image(code):
    filename = full_dir(code) + "/qr_code.jpg"

    qr_image = Image.open(filename)
    return qr_image


# Arrange an individual card image, like
#         +----------+----------+
#         |          |     id   |
#         |xxxxxxxxxx|  QR x x  |
#         |xxcoverxxx|  x xx    |
#         |xxxxxxxxxx|  xx  xx  |
#         |xxxxxxxxxx|  x x  x  |
#         |   title  |   title  |
#         |          |          |
#         +----------+----------+

def create_card_pattern(qr_code_img, cover_img, code, text):
    card = Image.new("RGB", (PATTERN_WIDTH, PATTERN_HEIGHT), (255,255,255))

    # put the cover image on the left side, taking up the full width and the proportionate height
    cover_width, cover_height = cover_img.size
    cover_img = cover_img.resize((CARD_WIDTH, int(cover_height * CARD_WIDTH / cover_width)), Image.LANCZOS)
    cover_width, cover_height = cover_img.size
    card.paste(cover_img, (0, int((CARD_HEIGHT - cover_height) / 2)))

    cover_img_bottom = int((CARD_HEIGHT + cover_height) / 2)


    # put the QR Code on the right side, taking up the full width and the proportionate height (but the QR code
    # has margin built in, so it won't actually take the full width)
    qr_code_width, qr_code_height = qr_code_img.size 
    qr_code_img = qr_code_img.resize((CARD_WIDTH, int(qr_code_height * CARD_WIDTH / qr_code_width)), Image.LANCZOS)
    qr_code_width, qr_code_height = qr_code_img.size 
    qr_code_top = int((CARD_HEIGHT - qr_code_height) / 2)
    qr_code_bottom = int((CARD_HEIGHT + qr_code_height) / 2)
    card.paste(qr_code_img, (CARD_WIDTH, qr_code_top))
    
    # Draw the rectangles, so that I know where to cut out
    carddraw = ImageDraw.Draw(card)
    carddraw.rectangle((0,0,CARD_WIDTH - 1, CARD_HEIGHT - 1), outline=(127,127,127))
    carddraw.rectangle((CARD_WIDTH,0,CARD_WIDTH*2 - 1, CARD_HEIGHT - 1), outline=(127,127,127))


    # Draw the text "QR####" on top of the qr code
    text_box(
        'QR{}'.format(code), 
        carddraw, 
        font(FONT_PATH, 16),
        (CARD_WIDTH + 60, qr_code_top - 20, CARD_WIDTH - 120, 20),
        horizontal_allignment = ALLIGNMENT_CENTER,
        vertical_allignment = ALLIGNMENT_BOTTOM,
        fill=(0,0,0)
    )
    # Draw the text for the given card under the Cover Image
    text_box(
        text, 
        carddraw, 
        font(FONT_PATH, 32),
        (60, cover_img_bottom + 30, CARD_WIDTH - 120, 20),
        horizontal_allignment = ALLIGNMENT_CENTER,
        vertical_allignment = ALLIGNMENT_TOP,
        fill=(0,0,0)
    )
    # Draw the text for the given card under the qr code
    text_box(
        text, 
        carddraw, 
        font(FONT_PATH, 32),
        (CARD_WIDTH + 60, qr_code_bottom, CARD_WIDTH - 120, 20),
        horizontal_allignment = ALLIGNMENT_CENTER,
        vertical_allignment = ALLIGNMENT_TOP,
        fill=(0,0,0)
    )
    # save the image!
    card.save(full_dir(code) + "/final.jpg")



@app.route('/s//QRCards')
@auth.login_required
def all_cards():
    card_infos = card.get_all_sorted()

    return render_template(
        'all_cards.html',
        cards=card_infos,
        type_names=TYPE_NAMES
    )

# This method generates a PDF for printing out multiple cards at a time
# it takes in an optional first and last GET parameter, with which to limit the cards displayed,
# and puts the cards 4-to-a-page into a PDF. The call to card.get_all_sorted ensures that
# the cards are displayed sorted primarily by type (track, album, artist, playlist, radio)
# and secondarily alphabetically by the "title"

@app.route('/s//QRCards.pdf')
@auth.login_required
def make_and_view_pdf():
    largest = card.get_largest_code()

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
    card_infos = card.get_all_sorted(first, last)

    CARDS_PER_PAGE = 4
    pages = split_list(list([info.code for info in card_infos]), CARDS_PER_PAGE)
    
    static_file = 'QRCards{}-{}.pdf'.format(first, last)
    
    file = '/home/pi/server/ghost_jukebox/static/{}'.format(static_file)
    
    for i, page in enumerate(pages):
        make_pdf_page(file, page, i == 0)

    return redirect(url_for('static', filename=static_file))

# This function just splits liszt into lists of no more than max_size length
def split_list(liszt, max_size):
    return [
        liszt[i*max_size : i*max_size + max_size] 
        for i in range(int(math.ceil(float(len(liszt))/max_size)))
    ]


# Arranges an individual page of cards, like:
#            +-------------+
#            |  +--+ +--+  |
#            |  +b-+ +d-+  |
#            |  +--+ +--+  |
#            |             |
#            |  +--+ +--+  |
#            |  +a-+ +c-+  |
#            |  +--+ +--+  |
#            +-------------+

def make_pdf_page(file, page, first):
    image_paths = ['{}/final.jpg'.format(full_dir(code)) for code in page]
    images = [Image.open(path) for path in image_paths]

    pdf_page = Image.new("RGB", (PAPER_HEIGHT, PAPER_WIDTH), (255,255,255))
    for i in range(len(images)):
        pdf_page.paste(images[i], PATTERN_LOCATIONS[i])

    pdf_page = pdf_page.transpose(Image.ROTATE_90)

    pdf_page.save(
        file,
        resolution = 300,
        title      = 'QR Cards',
        author     = 'The Ghost',
        append     = not first # Append this image to the PDF file if this is not the first, otherwise create the file
    )


""" 
The Text Box
Probably deserves its own place but I think it will only get used by this file
Oh Well

...

Draws the text <text> on the ImageDraw <image_draw> in the box (specified as a 4-ple of [x,y,width,height])
with the font <font> and the allignments as given. Passes other arguments to the ImageDraw.text function 
(for example, fill is a good one to use here). 
Can be used to center text horizontally and vertically, as well as right-align and bottom-allign (although it defaults to
left- and top-allignment). Nothing is done to prevent overflow, but the y and height values from the box will be used for vertical
allignment
Example usage:
    img = Image.new("RGB", (300,300), (255,255,255))
    img_draw = ImageDraw.Draw(img)
    text_box(
        "this is a text\n that respects linebreaks and will also break on spaces",
        img_draw,
        font("/Library/Fonts/Times New Roman Bold Italic.ttf", 16),
        (20, 20, 260,260),
        ALLIGNMENT_RIGHT,
        ALLIGNMENT_CENTER,
        fill=(255,0,255)
    )
    img.show()
"""


# The various allignments. 
# horizontal_allignment can take ALLIGNMENT_LEFT, ALLIGNMENT_CENTER, and ALLIGNMENT_RIGHT
# verical_allignment can take ALLIGNMENT_TOP, ALLIGNMENT_CENTER, and ALLIGNMENT_BOTTOM
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
        y = int(y + height / 2)
        y_offset = - (len(true_lines) * lineheight) / 2
    elif vertical_allignment == ALLIGNMENT_BOTTOM:
        y = int(y + height)
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

# helper function for fonts
def font(font_path, size=12):
    return ImageFont.truetype(font_path, size=size, encoding="unic")