# std lib
import argparse
from collections import defaultdict
import io
import os
from pathlib import Path
from pprint import pprint
import tarfile
from typing import Generator

# custom
from constants import (
    CLEAN_DESC,
    CLEAN_EPILOG,
    DICTIONARY,
    ENG_TARBALL,
    TARS,
    VOCAB_TARBALL)
from db_util import db_connect, add_column
from file_util import (
    divide_tarball,
    get_tar_data,
    remove_all_digits,
    remove_all_empty_elements,
    remove_all_punct,
    search,
    tar_contents)
from metrics_util import calculate_english_score, load_songs, word_set


if __name__ == "__main__":

    #Load description
    with open(CLEAN_DESC) as f:
        how_to_use = f.read()

    #Load epilog
    with open(CLEAN_EPILOG) as f:
        examples = f.read()

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=how_to_use, epilog=examples)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--checknames", action="store_true", help="Show how the names of the TarInfo objects conform to my naming convention (see README).")
    group.add_argument("--dbfield", action="store", nargs=2, type=str, metavar=("NAME", "TYPE"), help="Add a column to the DB with label NAME and type TYPE.")
    group.add_argument("--dividetarball", action="store", nargs=2, type=str, metavar=("TARBALL", "NUM"), help="Subdivide TARBALL into NUM smaller tarballs.")
    group.add_argument("--englishfilter", action="store", nargs=2, type=str, metavar=("TARBALL", "THRESHOLD"), help="Filter out songs below the THRESHOLD score from the input TARBALL.")
    group.add_argument("--popdb", action="store", nargs=2, type=str, metavar=("TARBALL", "DATABASE"), help="Create and populate DATABASE with artists and song names from compressed TARBALL.")
    group.add_argument("--vocab", action="store", nargs=1, type=str, metavar=("TARBALL"), help="Make a tarball that contains only unique word sets of the original lyrics in the given tarball.")

    args = parser.parse_args()

#POPULATE DB
    if args.popdb:
        if path(args.popdb[1]).exists():
            print("DB already exists. quitting...")
            quit()
        else:
            print("Creating db...")
            print("Adding artist and song name fields...")
            db, connection = db_connect(args.popdb[1])
            file_info = get_tar_data(args.popdb)
            db.executemany("insert into songs values (?,?)", file_info)
            connection.commit()
            connection.close()


#ADD DB FIELD
    elif args.dbfield:
        add_column(args.dbfield[0], args.dbfield[1])
        print(f"Added {args.dbfield[0]} column as type {args.dbfield[1]}")


#FILTER NON ENGLISH SONGS
    #TODO, something is wrong with how the tarball is created.
    elif args.englishfilter:
        tarname = args.englishfilter[0]
        user_score = int(args.englishfilter[1])
        assert type(user_score) == int
        assert type(tarname) == str

        #Setup for gathering metrics
        ref_dict = word_set(DICTIONARY)

        #Open tarballs
        english_tarball = tarfile.open(ENG_TARBALL, mode="w")
        songs = tarfile.open(f"{tarname}", mode="r", ignore_zeros=True)

        results = defaultdict(int)
        for song in enumerate(songs):
            lyrics = songs.extractfile(song[1])
            lyrics = lyrics.read().decode("utf-8")
            score = calculate_english_score(lyrics, ref_dict)

            if score >= user_score:
                data = songs.extractfile(song[1]) 
                extracted = data.read()
                english_tarball.addfile(song[1], io.BytesIO(extracted))
                results[score] += 1
                print(song[0], end="\r", flush=True)
        
        #Close tarballs
        songs.close()
        english_tarball.close()

        #Show results
        print()
        pprint(results)


#DIVIDE TARBALLS
    elif args.dividetarball:
#         print(args.dividetarball)
        name = args.dividetarball[0] 
        amt = int(args.dividetarball[1])
        assert amt > 1
        assert type(name) == str
        assert type(amt) == int
        divide_tarball(name, amt)


#MAKE VOCABULARY TARBALLS
    elif args.vocab:
        print(f"Opening '{args.vocab[0]}' and '{VOCAB_TARBALL}' ...")
        english_tarball = tarfile.open(args.vocab[0], mode="r")
        vocab_tarball = tarfile.open(VOCAB_TARBALL, mode="w")
        archives = english_tarball.getmembers()
        total_songs = len(archives)

        for song in enumerate(archives):
            lyrics = english_tarball.extractfile(song[1])
            lyrics = lyrics.read().decode("utf-8")

            #Normalize, prepare for archival
            #TODO, the order of the "remove" methods should not matter, but for some reason it does...
            set_ = set(lyrics.split())
            list_ = list(set_)
            list_ = [remove_all_digits(x) for x in list_]
            list_ = [remove_all_punct(x) for x in list_]
            list_ = remove_all_empty_elements(list_)
            list_ = [x.lower() for x in list_]
            list_ = sorted(list_)

            #TODO, put this in my notes, convert list to bytes

            #TODO, saving list like ["one", "two" ...] doesn't work well when extracting.
                # save it as one word per line like in a normal text file
#             str_ = str(list_).encode()
            str_ = "\n".join(list_).encode()


            bytes_obj = io.BytesIO(bytes(str_))
            info = tarfile.TarInfo(name=song[1].name)
            info.size = len(str_)
            vocab_tarball.addfile(info, bytes_obj)
            print(f"Archiving: {song[0]}/{total_songs}", end="\r", flush=True)

            #If enumerator > 2
#             if song[0] > 2:
#                 english_tarball.close()
#                 vocab_tarball.close()
#                 quit()
        english_tarball.close()
        vocab_tarball.close()


    #TODO, shouldn't this be part of the code that makes the english_only tarball?
    elif args.checknames:
        print("checking names...")
        #load combined.tar
