# std lib
import argparse
from collections import namedtuple
from pprint import pprint
import re
import tarfile
from typing import Generator
from typing import Any, Generator, List, TypeVar


# custom
from constants import (
    DEMO_DESC,
    DEMO_EPILOG,
    DEMO_TARBALL)
from search import (
    artist_search,
    song_search,
    lyric_search,
    regex_search,
    sentence_search)

tarData = TypeVar("tar", tarfile.TarFile, None)
match = TypeVar("match", re.match, None)
Song = namedtuple("Song", ["artist", "name"])


# Run Demo for demo argparser
#   Nat King Cole_A Blossom Fell.txt

#TODO, some songs cannot be extracted...


if __name__ == "__main__":

    #Load description
    with open(DEMO_DESC) as f:
        how_to_use = f.read()

    #Load epilog
    with open(DEMO_EPILOG) as f:
        examples = f.read()

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=how_to_use, epilog=examples)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--demo", action="store_true", help="Run interactive search on demo tarball.")

    args = parser.parse_args()

    if args.demo:
        print("Collecting demo archives...")
        options = ["artist", "song", "lyrics", "regex", "sentence"]
        songs = tarfile.open(DEMO_TARBALL)
        members = songs.getmembers()

        while True:
            pprint(options)
            user_answer = input(f"What do you want to search for?\nType 'q' to quit.\n")
            if user_answer == "artist":
                artist_search(songs, members)
            elif user_answer == "song":
                song_search(songs, members)
            elif user_answer == "lyrics":
                lyric_search(songs, members)
            elif user_answer == "regex":
                regex_search(songs, members)
            elif user_answer == "sentence":
                sentence_search(songs, members)
            elif user_answer == "q":
                break
            else:
                print(f"Choose one of {options}")
        songs.close()
        quit()
