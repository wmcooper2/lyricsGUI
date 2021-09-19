import sqlite3

con = sqlite3.connect("Databases/lyrics.db")
cur = con.cursor()

cur.execute("""create table if not exists songs(artist text, song text, lyrics text)""")

# next run this from the command line
# `sqlite3 lyrics.db`
#  sqlite3=> .import lyrics.csv songs
#  sqlite3=> .quit


cur.close()
con.close()
