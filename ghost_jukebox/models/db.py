import sqlite3
from flask import g
from ghost_jukebox import app, conf

DATABASE = conf.db_path

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, isolation_level=None)
    db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_one(query, args=()):
    print('SQL QUERY: {} {}'.format(query, args))
    app.logger.info('SQL QUERY: {} {}'.format(query, args))
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None)

def query_many(query, args=()):
    app.logger.info('SQL QUERY: {} {}'.format(query, args))
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return rv
