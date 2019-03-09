from ghost_jukebox.models.db import query_one
from flask import url_for

# Types:
SPOTIFY_TRACK    = 0
SPOTIFY_ALBUM    = 1
SPOTIFY_ARTIST   = 2
SPOTIFY_PLAYLIST = 3
ONLINE_RADIO     = 4

SPOTIFY_TYPES = [SPOTIFY_TRACK, SPOTIFY_ALBUM, SPOTIFY_ARTIST, SPOTIFY_PLAYLIST]

class QRInfo:
    def __init__(self, code, qrtype, uri, image):
        self.code = code
        self.qrtype = qrtype
        self.uri = uri 
        self.image_url = url_for(static, filename='qrimages/{}'.format(image))


def get_qr_info(code):
    row = query_one('SELECT code, type, uri, image_file FROM qr WHERE code = ?', [code])
    if row:
        return QRInfo(row[0], row[1], row[2], row[3])
    else:
        return None

def insert(qrinfo):
    query_one('INSERT INTO qr (code, type, uri, image_file) VALUES (?, ?, ?, ?)', [qrinfo.code, qrinfo.code, qrinfo.uri, qrinfo.image])

