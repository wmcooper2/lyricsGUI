#std lib
import re
import sqlite3


def connect():
    con = sqlite3.connect("Databases/demo.db")
    cur = con.cursor()
    return cur, con


def artist(name: str) -> list:
    cur, con = connect()
    cur.execute('SELECT song FROM demo WHERE artist=?', (name,))
    results = cur.fetchall()
    close_connection(cur, con)
    return [r[0] for r in results]


def artists() -> list:
    cur, con = connect()
    cur.execute('SELECT DISTINCT artist FROM demo')
    result = cur.fetchall()
    close_connection(cur, con)
    return result


def artist_count() -> int:
    cur, con = connect()
    cur.execute('SELECT COUNT(DISTINCT artist) FROM demo')
    result = cur.fetchall()[0][0]
    close_connection(cur, con)
    return result


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


#TODO, implement fuzzy search outside of db
def fuzzy_artist(name: str) -> list:
    cur, con = connect()
    lower = name.lower()
    sql_statement = f"SELECT song FROM demo WHERE LOWER(artist)='{lower}'"
    cur.execute(sql_statement)
    results = cur.fetchall()
    close_connection(cur, con)
    return [r[0] for r in results]


def fuzzy_artist_and_song(artist: str, song: str) -> str:
    """Returns the lyrics of a song by a specific artist."""
    cur, con = connect()
    sql_statement = f"SELECT lyrics FROM demo WHERE LOWER(artist)='{artist.lower()}' AND LOWER(song)='{song.lower()}'"
    print("sql: ", sql_statement)
    cur.execute(sql_statement)
    results = cur.fetchall()
    print("results:", results)
    close_connection(cur, con)
    try:
        return results[0][0]
    except IndexError:
        return []


def fuzzy_song_query(name: str) -> list:
    cur, con = connect()
    sql_statement = f"SELECT artist,song FROM demo WHERE LOWER(song)='{name.lower()}'"
    cur.execute(sql_statement)
    results = cur.fetchall()
    close_connection(cur, con)
    return results


def record_count() -> int:
    cur, con = connect()
    cur.execute('SELECT COUNT(*) FROM demo')
    result = cur.fetchall()[0][0]
    close_connection(cur, con)
    return result


def song_query(name: str) -> list:
    cur, con = connect()
    cur.execute('SELECT artist,song FROM demo WHERE song=?', (name,))
    results = cur.fetchall()
#     print("results:", results)
    close_connection(cur, con)
#     return [r[0] for r in results]
    return results


def _save(con) -> None:
    con.commit()


def close_connection(cur, con) -> None:
    cur.close()
    con.close()
