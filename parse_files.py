"""This module is meant to check the existing file names for any issues that would be troublesome for the database and prepare the lyrics files for insertion into the database."""

#std lib
from collections import namedtuple
import concurrent.futures
import logging
import pathlib
import pickle
from pprint import pprint
import re
import time
from typing import Callable, List, Tuple, Text

#custom
from parse_urls import load_pickle, save_text_file, pickle_file_records


FileRecord = namedtuple("FileRecord", ["artist", "song", "path"])



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


#TODO: TEST
def artist_song_from_file_name(file_name: str) -> Tuple[Text, Text]:
    """Returns artist name and song name from file path."""
    file_ = pathlib.Path(file_name)
    return file_.stem().split("_")


#TODO: TEST
def artist_song_from_paths(paths: List[pathlib.PosixPath]) -> List[FileRecord]:
    """Returns artist name and song name from file path."""
    records = []
    for index, path in enumerate(paths, start=1):
        try:
            artist, song = path.stem.split("_")
            records.append(FileRecord(artist, song, path))
        except ValueError:
            error = path.stem.split("_")
            logging.debug(f"Underscore Error: {error}")
        print(f"Progress: {index}", end="\r")
    print()
    return records






def create_file_records_from_dir(dir_: str, records: set) -> list:
    """Adds new records to 'records' from the file names in dir_.
        NOTE: Assumes that every file is a lyrics text file.
    """
    trouble_paths = []
    progress = 0
    for path in pathlib.Path(dir_).iterdir():
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


def load_file_records(file_name: str) -> set:
    """Loads FileRecords from 'file_name'."""
    # Ensure the file exists
    if not pathlib.Path(file_name).exists():
        pathlib.Path(file_name).touch()

    # Load the prior pickled data
    # if the file is empty, start by making a set
    try:
        records = load_pickle(file_name)
    except EOFError:
        records = set()
    
    # Convert pickled list into set of FileRecord types (my convention)
    if records:
        records = set([FileRecord(record[0], record[1], record[2]) for record in records])
    return records



def timing(function):
    """Timing decorator."""
    def wrapper(*args, **kwargs):
        start = time.time()
        function(*args, **kwargs)
        end = time.time()
        print("time taken:", function.__name__, end - start)
    return wrapper


def count_paths(dirs: list) -> None:
    paths = []
    for dir_ in dirs:
        for path in pathlib.Path(dir_).iterdir():
            paths.append(path)
#     print("path count:", len(paths))


def thread_get_file_name(path: pathlib.PosixPath) -> List[Text]:
    names = str(path.stem).split("_")
    return names


def process_get_file_name(path: str) -> List[Text]:
    path = pathlib.Path(path)
    names = str(path.stem).split("_")
    return names


def thread_count_words(path: pathlib.PosixPath) -> int:
    with open(str(path), "r") as f:
        try:
            data = f.read()
            return (len(data.split()),)
        except:
            #log the error
            return (None,)


# def process_count_words(path: str) -> int:
def process_count_words(path: str):
    with open(path, "r") as f:
        data = f.read()
        len(data.split())


@timing
def run_processes(files: list, funct):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = {executor.submit(funct, task) for task in files}
#         for future in concurrent.futures.as_completed(futures):
#             print(f"The outcome is {future.result()}")


@timing
def run_threads(files: list, funct):
    count = 0
    results = set()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(funct, task) for task in files}
        for future in concurrent.futures.as_completed(futures):
            results.add(tuple(future.result()))
            count += 1
            print(f"Progress: {count}", end="\r")
    print()
#     print(f"The outcome is {results}")
#     print()


def all_file_paths() -> List[pathlib.PosixPath]:
    # get all data dirs
    root_dir = "/Volumes/2021BLACK1TB/_DATA/LYRICS/lyrics for rpi_v1"
    sub_dirs = [path for path in pathlib.Path(root_dir).iterdir() if path.is_dir()]
    pprint(sub_dirs)

    # get all data subdirs
    all_dirs = []
    for path in sub_dirs:
        for sub_path in path.iterdir():
            if sub_path.is_dir():
                all_dirs.append(sub_path)
    pprint(all_dirs)

    # get file count 
    all_files = []
    count = 0
    for dir_ in all_dirs:
        for file_ in dir_.iterdir():
            if file_.suffix == ".txt":
                all_files.append(file_)
                count += 1
                print("Progress:", count, end="\r")
    return all_files


if __name__ == "__main__":
    logging.basicConfig(filename="Logs/file_names.errors", encoding="utf-8", level=logging.DEBUG)
    artist_song_paths = "Databases/artist_song_paths.pickle"
    file_block = "Databases/data9"

    # Load FileRecord Set
#     records = load_file_records(artist_song_paths)
#     records = create_file_records_from_dir(file_block, records)

    #Concurrency
#     print("Threaded Results:")
#     paths = all_file_paths()
#     run_threads(paths, thread_get_file_name)
#     run_threads(paths, thread_count_words)
    # conclusion: these two functions prove that the files can be reached, opened and tokenized

    #Pickling
#     paths = fileparser.all_file_paths()
#     records = fileparser.artist_song_from_paths(paths)
#     fileparser.pickle_file_records(file_records, records)
#     records = urlparser.load_pickle(file_records)
#     pprint(records[:10])
#     pprint(records[-10:])
    #conclusion: all but a few of the 600,000+ files have been created as FileRecords and pickled

