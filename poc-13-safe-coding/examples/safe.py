"""The same lookup through the safe abstraction. conformance.py reports nothing here."""
from safedb import SafeDB, identifier, placeholders, sql


def setup():
    db = SafeDB()
    db.script(sql(
        "CREATE TABLE albums (id TEXT, owner TEXT, title TEXT);"
        "INSERT INTO albums VALUES ('a1', 'alice', 'Holiday'), ('b7', 'bob', 'Private');"
    ))
    return db


def get_album(db, user, album_id):
    return db.query(sql("SELECT title FROM albums WHERE owner = ? AND id = ?"), user, album_id)


def get_albums(db, user, ids, sort="title"):
    # Awkward real-world cases the safe API must cover, or people will ask for exceptions:
    # a variable-length IN list and a caller-chosen sort column.
    q = (sql("SELECT title FROM albums WHERE owner = ? AND id IN") + placeholders(len(ids))
         + sql("ORDER BY") + identifier(sort, {"title", "id"}))
    return db.query(q, user, *ids)
