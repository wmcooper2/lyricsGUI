"""This module is meant to improve the parsing of artists and songs from the urls in order to fix the 'missing ending "t"' problem with earlier attempts."""

# std lib
from collections import namedtuple
import re
import sqlite3
import sys
import time
import urllib.parse as parser

# custom
from db_util import connect_to, close_connection, record_check

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
#     breakpoint()
    for index, url in enumerate(urls):
        record = artist_song_from_url(url)
#         print(f"Progress: {index},    Errors: {error_count}", end="\r")
        try:
            result = record_check(record.artist, record.song, cur)
            print(result, url)
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


if __name__ == "__main__":
    pass

    file_ = "support/songs.txt"
    with open(file_, "r") as f:
        urls = f.readlines()

    check_db_for_errors(urls)
#     record_creation_errors()
