import csv
import sqlite3
import sys

csv.field_size_limit(sys.maxsize)

con = sqlite3.connect("Databases/lyrics.db")
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS songs(id INTEGER PRIMARY KEY AUTOINCREMENT, artist TEXT, song TEXT, lyrics TEXT)""")

counter = 0
with open("Databases/lyrics.csv", "r") as f:
    data = csv.reader(f, delimiter="|")
    for row in data:
        row = [counter] + row
        cur.execute("""INSERT INTO songs VALUES(?, ?, ?, ?)""", row)
        counter += 1
        print(counter, end="\r")


con.commit()
cur.close()
con.close()
