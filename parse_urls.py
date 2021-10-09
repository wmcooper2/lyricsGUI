"""This module is meant to improve the parsing of artists and songs from the urls in order to fix the 'missing ending "t"' problem with earlier attempts."""

# std lib
from collections import namedtuple, defaultdict
import logging
import multiprocessing as mp
import os
from pprint import pprint
import pickle
import queue
import re
import sqlite3
import sys
import time
import urllib.parse as parser

# custom
import db_util

Record = namedtuple("Record", ["artist", "song", "url"])


def timing(function):
    """Timing decorator."""
    def wrapper(*args, **kwargs):
        start = time.time()
        function(*args, **kwargs)
        end = time.time()
        print("time taken:", end - start)
    return wrapper


def artist_song_from_url(url: str) -> Record:
    """Create a Record from the 'url'."""
    url = url.rstrip()
    normalized = parser.unquote_plus(url)  # convert from % to characters)
    regex = re.compile("[\d]+/")  # get index of last number place and slash
    match = regex.search(normalized)
    end = match.end()
    end_part = normalized[end:]
    artist, song = end_part.split("/")
    return Record(artist, song, url)
#     return (artist, song, url)


@timing
def record_creation_errors():
    """Check for errors in parsing Records from the urls."""
    errors = []
    error_count = 0
    for index, url in enumerate(urls):
        print("Progress:", index, end="\r")
        try:
            record = artist_song_from_url(url)
        except:
            error_count += 1
            logging.debug(f"URL parser: {record}")
    print("\nErrors:", error_count)


@timing
def check_db_for_errors(urls: list) -> None:
    cur, con = db_util.connect_to("Databases/lyrics.db")
    errors = []
    error_count = 0
    for index, url in enumerate(urls):
        record = artist_song_from_url(url)
        print(f"Progress: {index},    Errors: {error_count}", end="\r")
        try:
            result = db_util.record_check(record.artist, record.song, cur)
            if not result:
                error_count += 1
                errors.append(url)
        except KeyboardInterrupt:
            quit()
        except :
            error_count += 1
            errors.append(url)

    db_util.close_connection(cur, con)
    print("\nErrors:", error_count)
    if errors:
        file_ = "database_record_mismatch_errors.txt"
        with open(file_, "w+") as f:
            f.writelines(errors)

def create_records(urls: list):
    for index, url in enumerate(urls):
        print(f"Progress: {index}", end="\r")
        yield artist_song_from_url(url)


# def mp_info(record: Record, errors: list, error_count: int):
def mp_info(record: Record, lock: mp.Lock, index: int):
    """A multiprocess intended record lookup."""
    result = db_util.mp_record_check(record.artist, record.song)
    if not result:
        lock.acquire()
        with open("mp_errors.txt", "a+") as f:
            f.write(record.url+"\n")
        print(f"Error: ID:{os.getpid()}, {record}")
        lock.release()


@timing
def mp_check_db_for_errors(urls: list) -> None:
    """A multiprocess intended db error check."""
#     cur, con = db_util.connect_to("Databases/lyrics.db")
    errors = mp.Array("B", [10000])
    error_count = mp.Value("i", 0)
    q = mp.Queue()
    quit_flag = False
    records = create_records(urls)
    record_count = 0
#     pool = mp.Pool(5)
#     processes = mp.Queue()
#     processes = queue.Queue()
    lock = mp.Lock()


    while not quit_flag:
        processes = []
        while not q.full() and not quit_flag:
            #fill
            try:
                record = next(records)
            except StopIteration:
                quit_flag = True
                break

            record_count += 1
            print(f"Progress: {record_count}", end="\r")

            if record is None:
                quit_flag = True
                break
            q.put(record)
                
        while not q.empty():
            #drain
            
            task = q.get()
#             p = mp.Process(target=mp_info, args=(task, errors, error_count))
            p = mp.Process(target=mp_info, args=(task, lock, record_count))
            p.start()
#             processes.append(p)

#         for process in processes:
#             p.start()
#         for process in processes:
#             p.join()
#     pool.close()
#     pool.terminate()


def load_urls() -> list:
    input_file = "support/songs.txt"
    with open(input_file, "r") as f:
        return f.readlines()


def parse_unique_records(urls: list) -> list:
    unique_records = set()          
    for index, url in enumerate(urls):
        record = artist_song_from_url(url)
        unique_records.add(record)      #ex: Record(artist='!!! (Chk Chk Chk)', song='All U Writers', url='https://www.lyrics.com/lyric/32204994/%21%21%21+%28Chk+Chk+Chk%29/All+U+Writers')
        print("Progress:", index, end="\r")
    unique_records = list(unique_records)
    unique_records.sort()
    return unique_records


def artist_song_file_names(urls: list) -> list:
    file_names = set()
    for index, url in enumerate(urls):
        record = artist_song_from_url(url)
        file_names.add(f"{str(record.artist)}_{str(record.song)}")   #ex: '!!! (Chk Chk Chk)_All U Writers'
        print("Progress:", index, end="\r")
    file_names = list(file_names)
    file_names.sort()
    return file_names


def load_pickle(file_name: str) -> list:
    f = open(file_name, "rb")
    data = pickle.load(f)
    f.close()
    return data


def pickle_records(records: list) -> None:
    f = open("Databases/unique_records.pickle", "wb+")
    pickle.dump(records, f)
    f.close()


def pickle_artists(urls: list) -> None:
    artists = set()          
    for index, url in enumerate(urls):
        record = artist_song_from_url(url)
        artists.add(record.artist)
        print("Progress:", index, end="\r")
    artists = list(artists)
    artists.sort()
    f = open("Databases/unique_artists.pickle", "wb+")
    pickle.dump(artists, f)
    f.close()


def pickle_songs(urls: list) -> None:
    songs = set()          
    for index, url in enumerate(urls):
        record = artist_song_from_url(url)
        songs.add(record.song)
        print("Progress:", index, end="\r")
    songs = list(songs)
    songs.sort()
    f = open("Databases/unique_songs.pickle", "wb+")
    pickle.dump(songs, f)
    f.close()


def save_text_file(file_name: str, data: list) -> None:
    with open(file_name, "w+") as f:
        for line in data:
            f.write(line+"\n")


def pickle_artist_song_file_names(data: list) -> None:
    f = open("Databases/artist_song_file_names.pickle", "wb+")
    pickle.dump(data, f)
    f.close()


def pickle_file_records(file_name: str, data: list) -> None:
    f = open(file_name, "wb+")
    pickle.dump(data, f)
    f.close()



@timing
def run_threads(files: list, funct):
    results = set()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(funct, task) for task in files}
        for future in concurrent.futures.as_completed(futures):
            results.add(tuple(future.result()))
    print(f"The outcome is {results}")




if __name__ == "__main__":
    logging.basicConfig(filename="Logs/urlparser.log", encoding="utf-8", level=logging.DEBUG)
    #Load Original URLS
    urls = load_urls()

    #Parse URLS
#     records = parse_unique_records(urls)              # Good

    #Save Unique Artist_Song filenames to text file
    file_names = artist_song_file_names(urls)                                 # Good
    save_text_file("Databases/artist_song_file_names.txt", file_names)   # Good

    #Pickle Unique Artist_Song filenames
    pickle_artist_song_file_names(file_names)                                 # Good
#     records = load_pickle("Databases/artist_song_file_names.pickle")     # Good
#     print(records[1000:1010])
    
    #Error Checking
#     mp_check_db_for_errors(urls)                      # Too complicated
#     check_db_for_errors(urls)                         # Takes too long
#     record_creation_errors()                          # Good

    #Pickle Records
#     pickle_records(unique_records)
#     records = load_pickle("Databases/unique_records.pickle")     # Good
#     print("Loaded Pickle:", records[10000:10010])

    #Pickle Unique Artists
#     pickle_artists(urls)                                              # Good
#     records = load_pickle("Databases/unique_artists.pickle")     # Good
#     print("Loaded Pickle:", records[10000:10010])                     # Good


    #Pickle Unique Songs
#     pickle_songs(urls)
#     records = load_pickle("Databases/unique_songs.pickle")         # Good
#     print("Loaded Pickle:", records[10000:10010])                       # Good


    #If song and artist is not in the DB, then add them and their lyrics.
