from ghost_jukebox.models.db import query_one, query_many
from ghost_jukebox.models import info

QUEUE_POS = 'QUEUE_POS'
def get_queue_pos():
    try:
        return int(info.get_info(QUEUE_POS))
    except:
        return 0

def enqueue(thing):
    query_one('INSERT INTO queue(thing) VALUES (?)', [thing])

def pop():
    current_pos = get_queue_pos()
    row = query_one('SELECT thing FROM queue WHERE oid = ?', [current_pos])
    if not row or not row[0]:
        return None 
    else:
        info.set_info(QUEUE_POS, str(current_pos + 1))
        return row[0]