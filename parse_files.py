"""This module is meant to check the existing file names for any issues that would be troublesome for the database and prepare the lyrics files for insertion into the database."""

#std lib
from collections import namedtuple
import logging
from pathlib import Path
import pickle
from pprint import pprint
import re

#custom
from parse_urls import load_pickle, save_text_file, pickle_file_records


def split_file_name(file_name: str) -> list:
    """Get the artist and song from the file name."""
    name = re.sub(".txt", "", file_name)
    return name.split("_")


def underscore_check_okay(file_name: str) -> bool:
    """If there are not exactly 2 underscores in the name, returns False."""
    name = file_name.split("_")
    if len(name) == 2:
        return True
    return False


def create_file_records_from_dir(dir_: str, records: set) -> list:
    """Adds new records to 'records' from the file names in dir_.
        NOTE: Assumes that every file is a lyrics text file.
    """
    trouble_paths = []
    progress = 0
    for path in Path(dir_).iterdir():
        if not underscore_check_okay(path.stem):
            trouble_paths.append(path)
            logging.debug(f"Underscore Error: {path}")
        else:
            #create FileRecord
            artist, song = split_file_name(str(path.stem))
            records.add(FileRecord(artist, song, str(path)))
        progress += 1
        print(progress, end="\r")
    print(f"Errors: {len(trouble_paths)}")
    return records



if __name__ == "__main__":
    logging.basicConfig(filename="Logs/file_names.errors", encoding="utf-8", level=logging.DEBUG)
    FileRecord = namedtuple("FileRecord", ["artist", "song", "path"])
    artist_song_paths = "MetricsAndData/artist_song_paths.pickle"
    file_block = "Databases/data9"


    # Ensure the file exists
    if not Path(artist_song_paths).exists():
        Path(artist_song_paths).touch()

    # Load the prior pickled data
    # if the file is empty, start by making a set
    try:
        records = load_pickle(artist_song_paths)
    except EOFError:
        records = set()
    
    # Convert pickled list into set of FileRecord types (my convention)
    if records:
        records = set([FileRecord(record[0], record[1], record[2]) for record in records])


    # Create records from the collection of lyrics files
    records = create_file_records_from_dir(file_block, records)

    # Pickle the records
    # Convert to list of tuples
    #NOTE: Record needs __reduce__ method to make it picklable
    records = [(record.artist, record.song, record.path) for record in records]
    pickle_file_records(artist_song_paths, records)   # Good
