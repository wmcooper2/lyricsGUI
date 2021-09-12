#std lib
import asyncio

#3rd party
import psycopg2



def connect():
    con = psycopg2.connect("dbname=lyricsdemo user=postgres")
    cur = con.cursor()
    return cur, con


def artist(name: str) -> list:
    cur, con = connect()
    cur.execute('SELECT song FROM songs WHERE artist=%s', (name,))
    results = cur.fetchall()
    _close(cur, con)
    return [r[0] for r in results]


def artists() -> list:
    cur, con = connect()
    cur.execute('SELECT DISTINCT artist FROM songs')
    result = cur.fetchall()
    _close(cur, con)
    return result


def artist_count() -> int:
    cur, con = connect()
    cur.execute('SELECT COUNT(DISTINCT artist) FROM songs')
    result = cur.fetchall()[0][0]
    _close(cur, con)
    return result


def artist_and_song(artist: str, song: str) -> str:
    """Returns the lyrics of a song by a specific artist."""
    cur, con = connect()
    cur.execute('SELECT lyrics FROM songs WHERE artist=%s AND song=%s', (artist, song))
    results = cur.fetchall()
    _close(cur, con)
    return results[0][0]


def record_count() -> int:
    cur, con = connect()
    cur.execute('SELECT COUNT(*) FROM songs')
    result = cur.fetchall()[0][0]
    _close(cur, con)
    return result


def song_query(name: str) -> list:
    cur, con = connect()
    cur.execute('SELECT artist,song FROM songs WHERE song=%s', (name,))
    results = cur.fetchall()
    print("results:", results)
    _close(cur, con)
    return [r[0] for r in results]


def _save(con) -> None:
    con.commit()


def _close(cur, con) -> None:
    cur.close()
    con.close()
