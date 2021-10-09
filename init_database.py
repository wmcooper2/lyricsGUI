#std lib
import logging
from pathlib import Path
from pprint import pprint
import sqlite3
import sys

#custom
import db_util
import parse_urls as urlparser
import parse_files as fileparser


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
    artist_song_paths = "Databases/artist_song_paths.pickle"
    base_name = "lyrics_2021-10-03"
    logging.basicConfig(filename=f"Logs/{base_name}.errors", encoding="utf-8", level=logging.DEBUG)
    # db_util.populate_db_with_demo_data()
#     cur, con = db_util.connect_to(f"Databases/{base_name}.db")

    cur, con = db_util.connect()
    db_util.init_db_table(cur)
    paths = fileparser.all_file_paths()
    records = fileparser.artist_song_from_paths(paths)

    # pickle those records
    fileparser.pickle_file_records(artist_song_paths, records)
    db_util.close_connection(cur, con)

    # load pickle test
    records = urlparser.load_pickle(artist_song_paths)
    pprint(records[:10])
    pprint(records[-10:])
    #conclusion: all but a few of the 600,000+ files have been created as FileRecords and pickled

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

