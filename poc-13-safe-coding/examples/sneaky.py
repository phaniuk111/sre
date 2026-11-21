"""Attempts to get untrusted text into the query through sql(). conformance.py reports R2 on each."""
from safedb import SafeDB, sql


def by_fstring(db: SafeDB, user, album_id):
    return db.query(sql(f"SELECT title FROM albums WHERE owner = '{user}' AND id = '{album_id}'"))


def by_concat(db: SafeDB, user, album_id):
    return db.query(sql("SELECT title FROM albums WHERE id = '" + album_id + "'"))


def by_variable(db: SafeDB, text):
    return db.query(sql(text))
