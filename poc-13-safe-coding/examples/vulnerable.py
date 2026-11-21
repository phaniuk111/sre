"""What the safe abstraction replaces. conformance.py reports R1 on this file.

The album lookup should return a row only if the signed-in user owns it.
"""
import sqlite3


def setup():
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        "CREATE TABLE albums (id TEXT, owner TEXT, title TEXT);"
        "INSERT INTO albums VALUES ('a1', 'alice', 'Holiday'), ('b7', 'bob', 'Private');"
    )
    return conn


def get_album(conn, user, album_id):
    # Structure and data travel in one string. The database cannot tell them apart.
    q = "SELECT title FROM albums WHERE owner = '" + user + "' AND id = '" + album_id + "'"
    return conn.execute(q).fetchall()
