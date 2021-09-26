"""This module is meant to improve the parsing of artists and songs from the urls in order to fix the 'missing ending "t"' problem with earlier attempts."""

# std lib
from collections import namedtuple, defaultdict
import multiprocessing as mp
import os
import re
import sqlite3
import sys
import time
import urllib.parse as parser
import queue

# custom
from db_util import connect_to, close_connection, record_check, mp_record_check, all_artists_and_songs


Record = namedtuple("Record", ["artist", "song", "url"])



def timing(function):
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
    return Record(artist,song,url)


@timing
def record_creation_errors():
    errors = []
    error_count = 0
    for index, url in enumerate(urls):
        print("Progress:", index, end="\r")
        try:
            record = artist_song_from_url(url)
        except:
            error_count += 1
    print("\nErrors:", error_count)

    if errors:
        file_ = "record_creation_errors.txt"
        with open(file_, "w+") as f:
            f.writelines(errors)


@timing
def check_db_for_errors(urls: list) -> None:
    cur, con = connect_to("Databases/lyrics.db")
    errors = []
    error_count = 0
    for index, url in enumerate(urls):
        record = artist_song_from_url(url)
        print(f"Progress: {index},    Errors: {error_count}", end="\r")
        try:
            result = record_check(record.artist, record.song, cur)
            if not result:
                error_count += 1
                errors.append(url)
        except KeyboardInterrupt:
            quit()
        except :
            error_count += 1
            errors.append(url)

    close_connection(cur, con)
    print("\nErrors:", error_count)
    if errors:
        file_ = "database_record_mismatch_errors.txt"
        with open(file_, "w+") as f:
            f.writelines(errors)

def create_records():
    for index, url in enumerate(urls):
        print(f"Progress: {index}", end="\r")
        yield artist_song_from_url(url)


# def mp_info(record: Record, errors: list, error_count: int):
def mp_info(record: Record, lock: mp.Lock, index: int):
    result = mp_record_check(record.artist, record.song)
    if not result:
        lock.acquire()
        with open("mp_errors.txt", "a+") as f:
            f.write(record.url+"\n")
        print(f"Error: ID:{os.getpid()}, {record}")
        lock.release()


@timing
def mp_check_db_for_errors(urls: list) -> None:
#     cur, con = connect_to("Databases/lyrics.db")
    errors = mp.Array("B", [10000])
    error_count = mp.Value("i", 0)
    q = mp.Queue()
    quit_flag = False
    records = create_records()
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


    
if __name__ == "__main__":

    file_ = "support/songs.txt"
    with open(file_, "r") as f:
        urls = f.readlines()

#     mp_check_db_for_errors(urls)  #Too complicated
#     check_db_for_errors(urls)     #Takes too long

#     record_creation_errors()      #Good


    


    unique_records = set()
    unique_artist_songs = set()
    for index, url in enumerate(urls):
        record = artist_song_from_url(url)
        unique_records.add(record)
        unique_artist_songs.add(f"{str(record.artist)}|{str(record.song)}")
        print("Progress:", index, end="\r")


#     good_artists = defaultdict(default_factory=[])
#     for index, url in enumerate(urls):
#         print("Progress, good:", index, end="\r")
#         record = artist_song_from_url(url)
#         if record.artist not in good_artists:
#             good_artists[record.artist] = []
# 
#     print()
# 
#     bad_artists = defaultdict(default_factory=[])
#     for index, record in enumerate(all_artists_and_songs()):
#         print("Progress, bad:", index, end="\r")
#         if record[1] not in bad_artists:
#             bad_artists[record[1]] = []
#         bad_artists[record[1]].append(record[2])
# 
#     good_keys = good_artists.keys()
#     bad_keys = bad_artists.keys()
# 
#     print("len, bad artists:", len(bad_artists))
#     print("len, good artists:", len(good_artists))
# 
#     print("len, bad keys:", len(good_keys))
#     print("len, good keys:", len(bad_keys))
# 
# 
#     good_songs = 
#     for k,v in good_artists.items()
        
    


    
