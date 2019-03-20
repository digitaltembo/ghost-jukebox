from ghost_jukebox.models.db import query_one, query_many
from flask import url_for


def strify(number):
    return '{0:04d}'.format(number)

class CardInfo:
    def __init__(self, code, card_type, item_id, title):
        self.code = code
        self.card_type = card_type
        self.item_id = item_id
        self.title = title
    def static_dir(self):
        return "cards/qr{}".format(self.code)
    def image_src(self):
        return url_for("static", filename="{}/final.jpg".format(self.static_dir()))
    def view_link(self):
        return url_for('view_card', code=self.code)

def get_card_info(code):
    row = query_one('SELECT code, card_type, item_id, title FROM cards WHERE code = ?', [code])
    if row:
        return CardInfo(row[0], row[1], row[2], row[3])
    else:
        return None

def insert(card_info):
    query_one('''
        INSERT INTO cards (code, card_type, item_id, title) 
        VALUES (?, ?, ?, ?)
        ''', [card_info.code, card_info.card_type, card_info.item_id, card_info.title]
    )

def update(card_info):
    query_one('''
        UPDATE cards 
        SET
            card_type = ?,
            item_id   = ?,
            title     = ?
        WHERE
            code      = ?
        ''', [card_info.card_type, card_info.item_id, card_info.title, card_info.code]
    )

def get_all_sorted(first = 0, last = 10000):
    rows = query_many('''
        SELECT code, card_type, item_id, title 
        FROM cards 
        WHERE CAST(code AS int) >= ? AND CAST(code AS int) <= ?
        ORDER BY card_type ASC, title ASC
    ''', [first, last])

    card_infos = [CardInfo(row[0], row[1], row[2], row[3]) for row in rows]

    return card_infos


def get_largest_code():
    row = query_one('SELECT code FROM cards ORDER BY code DESC LIMIT 1')
    if row:
        return int(row[0])
    else:
        return 0

def get_next_code():
    return strify(get_largest_code() + 1)
