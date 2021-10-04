#std lib
import re
import sqlite3

# csv.field_size_limit(sys.maxsize)  # Increase field size limit
################################################################################
#   Demo DB
################################################################################
def connect():
    con = sqlite3.connect("Databases/demo.db")
    cur = con.cursor()
    return cur, con

#TODO: replaced with song_query()?
def artist(name: str) -> list:
    cur, con = connect()
    cur.execute('SELECT song FROM demo WHERE artist=?', (name,))
    results = cur.fetchall()
    close_connection(cur, con)
    return [r[0] for r in results]


def artist_query(name: str) -> list:
    """Get all artists who have a song 'name'."""
    cur, con = connect()
    cur.execute('SELECT artist,song FROM demo WHERE song=?', (name,))
    results = cur.fetchall()
    close_connection(cur, con)
    return results


#TODO: replaced with song_query()?
def artist2(name: str) -> list:
    cur, con = connect()
    cur.execute('SELECT artist,song FROM demo WHERE artist=?', (name,))
    results = cur.fetchall()
    close_connection(cur, con)
    return results


def artists() -> list:
    cur, con = connect()
    cur.execute('SELECT DISTINCT artist FROM demo')
    result = cur.fetchall()
    close_connection(cur, con)
    return result


# def artist_count() -> int:
#     cur, con = connect()
#     cur.execute('SELECT COUNT(DISTINCT artist) FROM demo')
#     result = cur.fetchall()[0][0]
#     close_connection(cur, con)
#     return result


def artist_and_song(artist: str, song: str) -> str:
    """Returns the lyrics of a song by a specific artist."""
    cur, con = connect()
    cur.execute('SELECT lyrics FROM demo WHERE artist=? AND song=?', (artist, song))
    results = cur.fetchall()
    close_connection(cur, con)
    try:
        return results[0][0]
    except IndexError:
        return []


def index_search(index: int, step: int) -> list:
    """Search for records starting at 'index'."""
    cur, con = connect()
    cur.execute('SELECT * FROM demo WHERE id>=? AND id<=?', (index, index+step))
    records = cur.fetchall()
    close_connection(cur, con)
    return records


#TODO, implement fuzzy search outside of db
def fuzzy_artist(artist: str) -> list:
    """Fuzzy search of 'artist'. Returns songs written by 'artist'."""
    cur, con = connect()
    sql_statement = f"SELECT artist,song FROM demo WHERE LOWER(artist)='{artist.lower()}'"
    cur.execute(sql_statement)
    results = cur.fetchall()
    close_connection(cur, con)
    return results


def fuzzy_artist_and_song(artist: str, song: str) -> str:
    """Fuzzy search for a 'song' by an 'artist'. Returns the lyrics."""
    cur, con = connect()
    sql_statement = f"SELECT lyrics FROM demo WHERE LOWER(artist)='{artist.lower()}' AND LOWER(song)='{song.lower()}'"
    cur.execute(sql_statement)
    results = cur.fetchall()
    close_connection(cur, con)
    try:
        return results[0][0]
    except IndexError:
        return []


def fuzzy_song(song: str) -> list:
    """Fuzzy search for 'song'. Returns list of artists and the song."""
    cur, con = connect()
    sql_statement = f"SELECT artist,song FROM demo WHERE LOWER(song)='{song.lower()}'"
    cur.execute(sql_statement)
    results = cur.fetchall()
    close_connection(cur, con)
    return results


def populate_db_with_demo_data() -> None:
    """Inserts about 60000 songs into the database"""
    counter = 0
    with open("Databases/demo.csv", "r") as f:
        data = csv.reader(f, delimiter="|")
        for row in data:
            print("data row:", row)
            row = [counter] + row
            cur.execute("""INSERT INTO songs VALUES(?, ?, ?, ?)""", row)
            counter += 1
            print(counter, end="\r")


def song_query(artist: str) -> list:
    """Get all songs from 'artist'."""
    cur, con = connect()
    cur.execute('SELECT artist,song FROM demo WHERE artist=?', (artist,))
    results = cur.fetchall()
    close_connection(cur, con)
    return results


################################################################################
#   Lyrics DB
################################################################################
#TODO, test
def mp_record_check(artist: str, song: str) -> bool:
    """Checks if a record exists in the database """
    cur, con = connect_to("Databases/lyrics.db")
    cur.execute('SELECT artist FROM songs WHERE artist=? AND song=?', (artist, song))
    results = cur.fetchall()
    close_connection(cur, con)
    return bool(results)


#TODO, test
def all_artists_and_songs() -> list:
    """Get all records' artist and song fields."""
    cur, con = connect_to("Databases/lyrics.db")
    cur.execute('SELECT * FROM songs;')
    records = cur.fetchall()
    close_connection(cur, con)
    return records


def record_check(artist: str, song: str, cur: sqlite3.Cursor) -> bool:
    """Checks if a record exists in the database """
    cur.execute('SELECT artist FROM songs WHERE artist=? AND song=?', (artist, song))
    results = cur.fetchall()
    return bool(results)


################################################################################
#   Shared Functions
################################################################################
def connect_to(db_name: str):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    return cur, con


def _save(con: sqlite3.Connection) -> None:
    con.commit()


def close_connection(cur: sqlite3.Cursor, con: sqlite3.Connection) -> None:
    _save(con)
    cur.close()
    con.close()


def record_count(db: str="demo") -> int:
    if db == "demo":
        cur, con = connect()
    else:
        cur, con = connect_to("Databases/lyrics.db")
    sql_statement = f'SELECT COUNT(*) FROM {db}'
    cur.execute(sql_statement)
    result = cur.fetchall()[0][0]
    close_connection(cur, con)
    return result


def init_db_table(cur: sqlite3.Cursor) -> None:
    cur.execute("""CREATE TABLE IF NOT EXISTS songs(id INTEGER PRIMARY KEY AUTOINCREMENT, artist TEXT NOT NULL, song TEXT NOT NULL, lyrics TEXT NOT NULL)""")


def get_highest_db_index(cur: sqlite3.Cursor, table: str) -> int:
    sql_statement = f"SELECT MAX(id) FROM {table}"
    result = cur.execute(sql_statement)
    result = result.fetchall()
    return result[0][0]



