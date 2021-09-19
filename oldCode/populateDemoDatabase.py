#stdlib
from pathlib import Path

#3rd party
import psycopg2

# Database
con = psycopg2.connect("dbname=lyricsdemo user=postgres")
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS songs (artist text, song text, lyrics text);""")


for file_ in Path("Databases/data9").iterdir():
    file_name = str(file_.name).split("_")
    artist = file_name[0]
    song = "".join(file_name[1:]).rstrip(".txt")
    with open(file_, "r") as f:
        lyrics = f.read()
        cur.execute("""INSERT INTO songs (artist, song, lyrics) VALUES (%s, %s, %s)""", (artist, song, lyrics))

con.commit()
cur.close()
con.close()






# EXAMPLES

# search in shell, single quotes are required in postgre
# SELECT song FROM songs WHERE artist='Kamelot';

# count records
# select count(*) from songs;
