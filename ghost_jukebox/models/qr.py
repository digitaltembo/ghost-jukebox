from ghost_jukebox.models.db import query_one
from flask import url_for

class QRInfo:
    def __init__(self, code, qrtype, uri, image):
        self.code = code
        self.qrtype = qrtype
        self.uri = uri 
        self.image_url = url_for('static', filename='qrimages/{}'.format(image))


def get_qr_info(code):
    row = query_one('SELECT code, type, uri, image_file FROM qr_codes WHERE code = ?', [code])
    if row:
        return QRInfo(row[0], row[1], row[2], row[3])
    else:
        return None

def get_next_code():
    row = query_one('SELECT code FROM qr_codes ORDER BY code DESC LIMIT 1')
    if row:
        current_code = int(row[0])
        next_code = '{0:04d}'.format(current_code + 1)
        return next_code 
    else:
        return '0000'

def insert(qrinfo):
    query_one('INSERT INTO qr_codes (code, type, uri, image_file) VALUES (?, ?, ?, ?)', [qrinfo.code, qrinfo.code, qrinfo.uri, qrinfo.image])


