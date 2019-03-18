from ghost_jukebox.models.db import query_one, query_many
from flask import url_for

class QRInfo:
    def __init__(self, code, qrtype, uri, title):
        self.code = code
        self.qrtype = qrtype
        self.uri = uri
        self.title = title


def get_qr_info(code):
    row = query_one('SELECT code, type, uri, title FROM qr_codes WHERE code = ?', [code])
    if row:
        return QRInfo(row[0], row[1], row[2], row[3])
    else:
        return None
def get_largest_code():
    row = query_one('SELECT code FROM qr_codes ORDER BY code DESC LIMIT 1')
    if row:
        return int(row[0])
    else:
        return 0
def strify(number):
    return '{0:04d}'.format(number)
def get_next_code():
    return strify(get_largest_code() + 1)

def insert(qrinfo):
    query_one('INSERT INTO qr_codes (code, type, uri, title) VALUES (?, ?, ?, ?)', [qrinfo.code, qrinfo.qrtype, qrinfo.uri, qrinfo.title])

def get_all_sorted(first = 0, last = 10000):
    rows = query_many('''
        SELECT code, type, uri, title 
        FROM qr_codes 
        WHERE CAST(code AS int) >= ? AND CAST(code AS int) <= ?
        ORDER BY type ASC, title ASC
    ''', [first, last])
    qrinfos = [QRInfo(row[0], row[1], row[2], row[3]) for row in rows]
    return qrinfos


