"""This module is meant to improve the parsing of artists and songs from the urls in order to fix the 'missing ending "t"' problem with earlier attempts."""
from collections import namedtuple
import re
import sys
import time
import urllib.parse as parser


Record = namedtuple("Record", ["artist", "song", "url"])

def timeit(function):
    def wrapper():
        start = time.time()
        function()
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


@timeit
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

if __name__ == "__main__":

    file_ = "support/songs.txt"
    with open(file_, "r") as f:
        urls = f.readlines()

    record_creation_errors()
