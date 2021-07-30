# std lib
from collections import defaultdict, namedtuple
from pathlib import Path
import re
import sqlite3
import string
import tarfile
from typing import Any, Generator, List, Set, TypeVar

# custom
from file_util import split_name

match = TypeVar("match", re.match, None)
tarData = TypeVar("tar", tarfile.TarFile, None)


def db_connect(database: str) -> [sqlite3.Cursor, sqlite3.Connection]:
    """Connect to DB."""
    assert type(database) == str
    try:
        db, connection = open_db(database)
        db.execute('''CREATE TABLE songs (artist text, name text)''')
        print("Created table 'Songs' in DB")
        return db, connection
    except sqlite3.OperationalError:
        print("DB already setup.")
    return db, connection


def open_db(database: str) -> [sqlite3.Cursor, sqlite3.Connection]:
    """Open a connection to the DB."""
    try:
        connection = sqlite3.connect(database)
        db = connection.cursor()
        return db, connection
    except:
        print("Couldn't open DB. Quitting...")
        quit()


def find_record(artist_name: str, song_name: str) -> str:
    """Find the record in the db."""
    db, connection = open_db("lyrics.db")
    return connection.execute(f"SELECT * FROM songs WHERE artist=? AND name=?", (artist_name, song_name))


#TODO, write tests from here
def add_column(name: str, type_: str) -> None:
    """Add a column to SQL DB."""
    db, connection = open_db("lyrics.db")
    connection.execute(f'''ALTER TABLE songs ADD {name} {type_};''')
    connection.commit()
    connection.close()


def add_score_to_db(db: Any, english_score: int, song: str) -> sqlite3.Cursor:
    """Add the english_score to the DB."""
    db, connection = open_db("lyrics.db")
    artist, song = split_name(song)
    artist = re.sub("^block[0-9]{,3}/", "", artist)
#     print(f"SEARCH :{english_score} {artist} // {song}")
    connection.execute('''UPDATE songs SET englishscore=? WHERE artist=? AND name=?''', (english_score, artist, song))
    connection.commit()
