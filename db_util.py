#std lib
import re
import sqlite3


def connect():
    con = sqlite3.connect("Databases/lyrics.db")
    cur = con.cursor()
    return cur, con


def artist(name: str) -> list:
    cur, con = connect()
    cur.execute('SELECT song FROM songs WHERE artist=?', (name,))
    results = cur.fetchall()
    close_connection(cur, con)
    return [r[0] for r in results]


def artists() -> list:
    cur, con = connect()
    cur.execute('SELECT DISTINCT artist FROM songs')
    result = cur.fetchall()
    close_connection(cur, con)
    return result


def artist_count() -> int:
    cur, con = connect()
    cur.execute('SELECT COUNT(DISTINCT artist) FROM songs')
    result = cur.fetchall()[0][0]
    close_connection(cur, con)
    return result


def artist_and_song(artist: str, song: str) -> str:
    """Returns the lyrics of a song by a specific artist."""
    cur, con = connect()
    cur.execute('SELECT lyrics FROM songs WHERE artist=? AND song=?', (artist, song))
    results = cur.fetchall()
    close_connection(cur, con)
    try:
        return results[0][0]
    except IndexError:
        return []


def record_count() -> int:
    cur, con = connect()
    cur.execute('SELECT COUNT(*) FROM songs')
    result = cur.fetchall()[0][0]
    close_connection(cur, con)
    return result


def song_query(name: str) -> list:
    cur, con = connect()
    cur.execute('SELECT artist,song FROM songs WHERE song=?', (name,))
    results = cur.fetchall()
    print("results:", results)
    close_connection(cur, con)
    return [r[0] for r in results]


def _save(con) -> None:
    con.commit()


def close_connection(cur, con) -> None:
    cur.close()
    con.close()
