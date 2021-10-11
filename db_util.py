#std lib
import logging
import re
import sqlite3
from typing import List, Text, Tuple

#custom
import parse_urls as urlparser


# csv.field_size_limit(sys.maxsize)  # Increase field size limit
################################################################################
#   Demo DB
################################################################################
def connect() -> Tuple[sqlite3.Cursor, sqlite3.Connection]:
    con = sqlite3.connect("Databases/lyrics.db")
    cur = con.cursor()
    return cur, con

#TODO: replaced with song_query()?
def artist(table: Text, name: Text) -> List:
    cur, con = connect()
    cur.execute(f"SELECT song FROM {table} WHERE artist=?", (name,))
    results = cur.fetchall()
    close_connection(cur, con)
    return [r[0] for r in results]


def artist_query(database: Text, table: Text, name: Text) -> list:
    """Get all artists who have a song 'name'."""
    cur, con = connect()
    cur.execute(f"SELECT artist,song FROM {table} WHERE song=?", (name,))
    results = cur.fetchall()
    close_connection(cur, con)
    return results


#TODO: replaced with song_query()?
def artist2(table: Text, name: Text) -> list:
    cur, con = connect()
    cur.execute(f"SELECT artist,song FROM {table} WHERE artist=?", (name,))
    results = cur.fetchall()
    close_connection(cur, con)
    return results


def artists(table: Text) -> List:
    cur, con = connect()
    cur.execute(f"SELECT DISTINCT artist FROM {table}")
    result = cur.fetchall()
    close_connection(cur, con)
    return result


# def artist_count(database: Text) -> int:
#     cur, con = connect()
#     cur.execute('SELECT COUNT(DISTINCT artist) FROM demo')
#     result = cur.fetchall()[0][0]
#     close_connection(cur, con)
#     return result


def artist_and_song(database: Text, table: Text, artist: Text, song: Text) -> Text:
    """Returns the lyrics of a song by a specific artist."""
    cur, con = connect()
    cur.execute(f"SELECT lyrics FROM {table} WHERE artist=? AND song=?", (artist, song))
    results = cur.fetchall()
    close_connection(cur, con)
    try:
        return results[0][0]
    except IndexError:
        return []


def index_search(database: Text, table: Text, index: int, step: int) -> List:
    """Search for records starting at 'index'."""
    cur, con = connect()
    cur.execute(f"SELECT * FROM {table} WHERE id>=? AND id<=?", (index, index+step))
    records = cur.fetchall()
    close_connection(cur, con)
    return records


#TODO, implement fuzzy search outside of db
def fuzzy_artist(database: Text, table: Text, artist: Text) -> List:
    """Fuzzy search of 'artist'. Returns songs written by 'artist'."""
    cur, con = connect()
    sql_statement = f"SELECT artist,song FROM {table} WHERE LOWER(artist)='{artist.lower()}'"
    cur.execute(sql_statement)
    results = cur.fetchall()
    close_connection(cur, con)
    return results


def fuzzy_artist_and_song(database: Text, table: Text, artist: Text, song: Text) -> Text:
    """Fuzzy search for a 'song' by an 'artist'. Returns the lyrics."""
    cur, con = connect()
    sql_statement = f"SELECT lyrics FROM {table} WHERE LOWER(artist)='{artist.lower()}' AND LOWER(song)='{song.lower()}'"
    cur.execute(sql_statement)
    results = cur.fetchall()
    close_connection(cur, con)
    try:
        return results[0][0]
    except IndexError:
        return []


def fuzzy_song(database: Text, table: Text, song: Text) -> List:
    """Fuzzy search for 'song'. Returns list of artists and the song."""
    cur, con = connect()
    sql_statement = f"SELECT artist,song FROM {table} WHERE LOWER(song)='{song.lower()}'"
    cur.execute(sql_statement)
    results = cur.fetchall()
    close_connection(cur, con)
    return results


#TODO: rename to be more flexible with the debug choice at the top of this module
def populate_db_with_demo_data() -> None:
    """Inserts about 60000 songs into the database"""
    counter = 0
    with open(f"Databases/{DB}.csv", "r") as f:
        data = csv.reader(f, delimiter="|")
        for row in data:
            print("data row:", row)
            row = [counter] + row
            cur.execute("""INSERT INTO {TABLE} VALUES(?, ?, ?, ?)""", row)
            counter += 1
            print(counter, end="\r")


def song_query(database: Text, table: Text, artist: Text) -> List:
    """Get all songs from 'artist'."""
    cur, con = connect()
    cur.execute(f"SELECT artist,song FROM {table} WHERE artist=?", (artist,))
    results = cur.fetchall()
    close_connection(cur, con)
    return results


################################################################################
#   Lyrics DB
################################################################################
#TODO, test
def mp_record_check(artist: Text, song: Text) -> bool:
    """Checks if a record exists in the database """
    cur, con = lyrics_db()
    cur.execute(f"SELECT artist FROM {TABLE} WHERE artist=? AND song=?", (artist, song))
    results = cur.fetchall()
    close_connection(cur, con)
    return bool(results)


#TODO, test
def all_artists_and_songs(database: Text, table: Text) -> List:
    """Get all records' artist and song fields."""
    cur, con = lyrics_db()
    cur.execute(f"SELECT * FROM {table}")
    records = cur.fetchall()
    close_connection(cur, con)
    return records


def record_check(table: Text, artist: Text, song: Text, cur: sqlite3.Cursor) -> bool:
    """Checks if a record exists in the database """
    cur.execute(f"SELECT artist FROM {table} WHERE artist=? AND song=?", (artist, song))
    results = cur.fetchall()
    return bool(results)


################################################################################
#   Shared Functions
################################################################################
def lyrics_db():
    con = sqlite3.Connection("Databases/lyrics.db")
    cur = con.cursor()
    return cur, con


def _save(con: sqlite3.Connection) -> None:
    con.commit()


def close_connection(cur: sqlite3.Cursor, con: sqlite3.Connection) -> None:
    _save(con)
    cur.close()
    con.close()


def record_count(database: Text, table: Text) -> int:
    cur, con = lyrics_db()
    sql_statement = f"SELECT COUNT(*) FROM {table}"
    cur.execute(sql_statement)
    result = cur.fetchall()[0][0]
    close_connection(cur, con)
    return result


def init_db_table(cur: sqlite3.Cursor) -> None:
    cur.execute(f"CREATE TABLE IF NOT EXISTS {TABLE}(id INTEGER PRIMARY KEY AUTOINCREMENT, artist TEXT NOT NULL, song TEXT NOT NULL, lyrics TEXT NOT NULL)")


def get_highest_db_index(cur: sqlite3.Cursor, table: Text) -> int:
    sql_statement = f"SELECT MAX(id) FROM {table}"
    result = cur.execute(sql_statement)
    result = result.fetchall()
    return result[0][0]


def all_file_records_in_db():
    file_records = "Databases/file_records.pickle"
    print(f"Loading pickle: {file_records}")
    records = urlparser.load_pickle(file_records)
    for index, record in enumerate(records, start=1):
        lyrics = artist_and_song(record.artist, record.song)
        print(f"Progress: {index}", end="\r")
        if not lyrics:
            logging.debug(f"Record not found in DB: {record}")
    print()






if __name__ == "__main__":
    base_name = "db_health"
    logging.basicConfig(filename=f"Logs/{base_name}.errors", encoding="utf-8", level=logging.DEBUG)

################################################################################
#   Database Checks
################################################################################
    #are the new records that were created from the text files exist in the DB?
#     all_file_records_in_db()
    # conclusion: after 1000 queries, 139 were errors. I stopped the program because that's 
    #   just too many. I will have to rebuild the DB from the original records.


    # load the FileRecords
    file_record_pickle = "Databases/file_records.pickle"
    print(f"Loading pickle: {file_record_pickle}")
    file_records = urlparser.load_pickle(file_record_pickle)

    # load the URLRecords
#     url_record_pickle = "Databases/artist_song_paths.pickle"
#     print(f"Loading pickle: {url_record_pickle}")
#     url_records = urlparser.load_pickle(url_record_pickle)

    # create set of artist song from URLRecords
    # create set of artist song from FileRecords
    # find the disjoint of the two
    # save that to a log



