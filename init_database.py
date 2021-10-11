#std lib
from collections import namedtuple
import logging
from pathlib import Path
from pprint import pprint
import sqlite3
import sys

#custom
import db_util
import parse_urls as urlparser
import parse_files as fileparser

URLRecord = namedtuple("URLRecord", ["artist", "song", "url"])
FileRecord = namedtuple("FileRecord", ["artist", "song", "path"])

def add_data_block_to_db(block: str, records: list, cur: sqlite3.Cursor, index: int=1) -> None:
    progress = 0
    errors = 0
    for path in Path(block).iterdir():
        try:
            artist, song = path.stem.split("_")
        except ValueError:
            # too many underscores in name
            logging.debug(f"Too many underscores: {str(path)}")
        new_file_name = f"{artist}|{song}"
        lyrics = None
        if new_file_name in records:
            with open(str(path), "r") as f:
                lyrics = f.read()
            record = [index, artist, song, lyrics]
            cur.execute("""INSERT INTO songs VALUES(?, ?, ?, ?)""", record)
        else:
            logging.debug(f"Not found in records: {str(path)}")
            errors += 1
        index += 1
        progress += 1
        print(f"Progress: {progress}, Errors: {errors}", end="\r")
    print()

if __name__ == "__main__":
    file_records = "Databases/file_records.pickle"
    base_name = "lyrics_2021-10-03"
    logging.basicConfig(filename=f"Logs/{base_name}.errors", encoding="utf-8", level=logging.DEBUG)
    # db_util.populate_db_with_demo_data()
#     cur, con = db_util.lyrics_db()

#     cur, con = db_util.connect()
#     db_util.init_db_table(cur)
#     #do stuff
#     db_util.close_connection(cur, con)

#     records = parser.load_pickle("Databases/artist_song_file_names.pickle")
#     #start here
#     # get max index of last db entry
#     index = db_util.get_highest_db_index(cur, "songs")
#     if index is None:
#         index = 1
#         raise Exception("Error: is the table empty? The index should not be 0 otherwise.")
#         quit()
# 
#     add_data_block_to_db("Databases/data9", records, cur, index)
#     db_util.close_connection(cur, con)


    #Check FileRecord set against URLRecord set
    # load both pickles
    file_ = "file_records"
    print(f"Loading: {file_}")
    file_records = urlparser.load_pickle(file_)

    file_ = "url_records"
    print(f"Loading: {file_}")
    url_records = urlparser.load_pickle(file_)

    ########## Sets
    # convert to sets
    print("Converting to sets...")
    file_set = set([(record.artist, record.song) for record in file_records])
    url_set = set([(record.artist, record.song) for record in url_records])


    ########## Symmetric Difference
    difference = file_set.symmetric_difference(url_set)
    print(f"Symmetric Difference, records: {len(difference)}")

    file_artists = set([record.artist for record in file_records])
    url_artists = set([record.artist for record in url_records])
    difference = file_artists.symmetric_difference(url_artists)
    print(f"Symmetric Difference, artists: {len(difference)}")

    file_songs = set([record.song for record in file_records])
    url_songs = set([record.song for record in url_records])
    difference = file_songs.symmetric_difference(url_songs)
    print(f"Symmetric Difference, songs: {len(difference)}")




    ########## Artists
    in_file_not_url = file_artists.difference(url_artists)
    print(f"Artists in file_records not in url_records: {len(in_file_not_url)}")
    in_file_not_url = sorted(list(in_file_not_url))
    pprint(in_file_not_url[:10])


    in_url_not_file = url_artists.difference(file_artists)
    print(f"Artists in url_records not in file_records: {len(in_url_not_file)}")
    in_url_not_file = sorted(list(in_url_not_file))
    pprint(in_url_not_file[:10])
