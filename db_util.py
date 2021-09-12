#std lib
import asyncio

#3rd party
import psycopg2



def connect():
    con = psycopg2.connect("dbname=lyricsdemo user=postgres")
    cur = con.cursor()
    return cur, con

def artists() -> list:
    cur, con = connect()
    cur.execute('select distinct artist from songs')
    result = cur.fetchall()
    _close(cur, con)
    return result

def artist_count() -> int:
    cur, con = connect()
    cur.execute('select count(distinct artist) from songs')
    result = cur.fetchall()[0][0]
    _close(cur, con)
    return result

def record_count() -> int:
    cur, con = connect()
    cur.execute('select count(*) from songs')
    result = cur.fetchall()[0][0]
    _close(cur, con)
    return result

def _save(con) -> None:
    con.commit()

def _close(cur, con) -> None:
    cur.close()
    con.close()
