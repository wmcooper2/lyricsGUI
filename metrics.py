# std lib
from pprint import pprint
from time import time
from timeit import timeit
from typing import Callable


# custom
from db_util import (
    add_score_to_db,
    open_db)
from metrics_util import (
    calculate_english_score,
    load_songs,
    save_word_list,
    word_set)


#ARGPARSE
#     group.add_argument("--estimatetime", action="store_true", help="Estimate the time required to run the code on the entire collection of songs.")

    #todo, move this into a separate cli tool
#     elif args.estimatetime:
#         print("estimating time to complete")



# def english_score(tarname: str):
#     """Add a score to the DB based on the ratio of English words found in 'tarname' files."""
#     manually_curated = "manually_curated_words.txt"
#     dictionary = "/usr/share/dict/web2"

    # setup for gathering metrics
#     ref_dict = word_set(dictionary)
#     bad_words = word_set(manually_curated)
#     songs = load_songs(tarname)  # gen songs

#     counter = 0
#     for song in songs:
#         score = calculate_english_score(song, ref_dict)
    #     bad_words = not_found.union(bad_words)
#         add_score_to_db(db, score, song[1])
#         counter += 1
#         print(f"Songs scored : {counter}", end="\r", flush=True)

    # testing
#         if counter >= 5:
#             break


def add_english_score_to_db(tarname: str):
    """Add a score to the DB based on the ratio of English words found in 'tarname' files."""
    manually_curated = "manually_curated_words.txt"
    dictionary = "/usr/share/dict/web2"

    # setup for gathering metrics
    ref_dict = word_set(dictionary)
    bad_words = word_set(manually_curated)
    db, connection = open_db("lyrics.db")
    songs = load_songs(tarname)  # gen of songs

    # This whole block's purpose is to calculate the good English words, and add it to the DB
    counter = 0
    for song in songs:
        score = calculate_english_score(song, ref_dict)
    #     bad_words = not_found.union(bad_words)
        add_score_to_db(db, score, song[1])
        counter += 1
        print(f"Songs scored : {counter}", end="\r", flush=True)

    # testing
#         if counter >= 5:
#             break

    #Close DB
    connection.commit()
    connection.close()



#TODO
#Read a file from the database
#give a score and save to DB
# save_word_list(manually_curated, bad_words)

#Timing a function, make the timing setup a decorator
# start = time()
#Put function here
# end = time()
# time_taken = (end-start)/60
# total_songs = 616500
# print(f"Time taken: {round(time_taken, 6)} minutes")
# print(f"Estimated Time (600,000+ songs): {round(((total_songs/counter)*time_taken)/60)} hours")
