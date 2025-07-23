import sqlite3
from flask import g, current_app

def get_db_connection():
    if 'db' not in g:
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row

    
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)