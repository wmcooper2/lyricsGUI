# std lib
import argparse
from collections import namedtuple, defaultdict
import csv
from datetime import datetime
from pprint import pprint
import re
import tarfile
from typing import Any, Generator, List, TypeVar


# 3rd party
from tabulate import tabulate


# custom
from constants import (
    ENG_TARBALL,
    RESULTS,
    SEARCH_DESC,
    SEARCH_EPILOG,
    UNCOMPRESSED_TESTING,
    VOCAB_TARBALL)
from metrics_util import edit_distance
from file_util import remove_all_digits, remove_all_punct


Args = TypeVar("Args", argparse.Namespace, None)
match = TypeVar("match", re.match, None)
Song = namedtuple("Song", ["artist", "name"])
tarData = TypeVar("tar", tarfile.TarFile, None)


#TODO
# check if a search was already performed by looking for the search string in the title of the results file then ask the user if they want to proceed.
# are the --song and --lyrics options the same thing?

# @profile
def artist_search(songs: tarData, members: List):
    request = input("What artist? ")
    member_count = len(members)

    #Normalize user request
    print(f"Searching for '{request}'")
    user_request = remove_all_digits(request)
    user_request = remove_all_punct(user_request)
    user_request = user_request.lower()

    results = []
    for member in enumerate(members):
        #Clean up title
        artist, song = member[1].name.rstrip(".txt").split("_")

        #normalize the strings for comparison
        artist = remove_all_digits(artist)
        artist = remove_all_punct(artist)
        artist = artist.lower()
        edit_score = edit_distance(user_request, artist)

        #songs may share the same name, keep all
        artist, song = member[1].name.rstrip(".txt").split("_")
        results.append((artist, song, edit_score))
        print(f"{member[0]}/{member_count}", end="\r", flush=True)

    #sort list of matches by value
    top_100 = sorted(results, key=lambda x: x[2])
    top_100 = top_100[:100]

    #Save to results/
    timestamp = "{:%Y-%b-%d %H:%M:%S}".format(datetime.now())
    with open(f"{RESULTS}{request}_{timestamp}.txt", "w+") as save_to:
        save_to.write(tabulate(top_100))

    print("\nA smaller Edit Distance means a closer match.")
    top_10 = top_100[:10]
    print(tabulate((top_10), headers=["Artist", "Song", "Edit Distance"]))


def lyric_search(songs: tarData, members: List):
    """Search for the lyrics of a song."""
    request = input("What song? ")
    member_count = len(members)

    #Normalize user request
    print(f"Searching for '{request}'")
    user_request = remove_all_digits(request)
    user_request = remove_all_punct(user_request)
    user_request = user_request.lower()

    results = []
    for member in enumerate(members):
        #Clean up title
        artist, song = member[1].name.rstrip(".txt").split("_")

        #normalize the strings for comparison
        song = remove_all_digits(song)
        song = remove_all_punct(song)
        song = song.lower()
        edit_score = edit_distance(user_request, song)

        #songs may share the same name, keep all
        artist, song = member[1].name.rstrip(".txt").split("_")
        results.append((artist, song, edit_score))
        print(f"{member[0]}/{member_count}", end="\r", flush=True)

    top_100 = sorted(results, key=lambda x: x[2])
    last_100 = top_100[-100:]
    top_100 = top_100[:100]

    #Show results, have user pick one to show
    print("\nA smaller Edit Distance means a closer match.")
    top_10 = [[x[0], x[1][0], x[1][1], x[1][2]] for x in enumerate(top_100[:10])]
    print(tabulate((top_10), headers=["Index", "Artist", "Song", "Edit Distance"]))

    #Extract to memory and print to the screen
    while True:
        view_extract = input("View [v], extract [e] to dir or quit [q]? ")
        if view_extract == "v":
            answer = int(input("Which one do you want to view? [index #] "))
            artist = top_10[answer][1]

            #TODO, error says here, but...
            song = top_10[answer][2]
            title = f"{artist}_{song}.txt"
            text = songs.extractfile(title).read().decode("utf-8")
            header = f"\n{artist}, {song}"
            print(header)
            print("-"*len(header))
            print(text)
        elif view_extract == "e":
            #TODO, Give user option to save file to a dir
            dir_ = input("extract to where? ")
            print(f"Extracting to {dir_}")
            break
        elif view_extract == "q":
            break
        else:
            print("Choose one of [veq].")



def interactive_search():
    """An interactive search tool."""
    print("Collecting archives...")
    options = ["artist", "song", "lyrics", "regex", "sentence"]
    songs = tarfile.open(ENG_TARBALL)
#     songs = tarfile.open(UNCOMPRESSED_TESTING)
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


def song_search(songs: tarData, members: List):
    """Search for the title of a song."""
    request = input("What song? ")
    member_count = len(members)

    #Normalize user request
    print(f"Searching for '{request}'")
    user_request = remove_all_digits(request)
    user_request = remove_all_punct(user_request)
    user_request = user_request.lower()

    results = []
    for member in enumerate(members):
        #Clean up title
        artist, song = member[1].name.rstrip(".txt").split("_")

        #normalize the strings for comparison
        song = remove_all_digits(song)
        song = remove_all_punct(song)
        song = song.lower()
        edit_score = edit_distance(user_request, song)

        #songs may share the same name, keep all
        artist, song = member[1].name.rstrip(".txt").split("_")
        results.append((artist, song, edit_score))
        print(f"{member[0]}/{member_count}", end="\r", flush=True)

    #sort list of matches by value
    top_100 = sorted(results, key=lambda x: x[2])
    top_100 = top_100[:100]

    #Save to results/
    timestamp = "{:%Y-%b-%d %H:%M:%S}".format(datetime.now())
    with open(f"{RESULTS}{request}_{timestamp}.txt", "w+") as save_to:
        save_to.write(tabulate(top_100))

    print("\nA smaller Edit Distance means a closer match.")
    top_10 = top_100[:10]
    print(tabulate((top_10), headers=["Artist", "Song", "Edit Distance"]))


def regex_search(songs: tarData, members: List):
    """Basically, this block is supposed to be the same as a regular sentence search,
        but uses a case-insensitive regex in its place."""
    regex = input("Enter a regex: ")
    save_name = input("Enter a user-friendly file name: ") 
    member_count = len(members)
    pattern = re.compile(regex, re.IGNORECASE)

    print(f"Searching for '{regex}'")
    results = defaultdict(int)
    for member in enumerate(members):
        lyrics = songs.extractfile(member[1])

        lyrics = lyrics.read().decode("utf-8")
        match_count = len(pattern.findall(lyrics))

        #save count of all occurrences in list, use bisect to insert based on count
        print(f"{member[0]}/{member_count}", end="\r", flush=True)

        # if any matches
        if match_count > 0:
            name = member[1].name.rstrip(".txt")
            results[name] += match_count

    #sort list of matches by value
    results = list(results.items())
    top_100 = sorted(results, key=lambda x: x[1], reverse=True)
    top_100 = top_100[:100]

    #Save to results/
    timestamp = "{:%Y-%b-%d %H:%M:%S}".format(datetime.now())
    with open(f"{RESULTS}{save_name}_{timestamp}.csv", "w+") as save_to:
        writer = csv.writer(save_to, delimiter="|")
        for result in top_100:
            artist, song = result[0].split("_")
            match_count = result[1]
            row = [artist, song, str(match_count)]
            try:
                writer.writerow(row)
            except:
                continue
    print(f"\nSearch for '{regex}' finished.")


def sentence_search(songs: tarData, members: List):
    """Search for exact sentence or exact word."""
    request = input("What sentence/word are you looking for? ")
    songs = tarfile.open(ENG_TARBALL)
#     songs = tarfile.open(UNCOMPRESSED_TESTING)
    pattern = re.compile(request, re.IGNORECASE)
    member_count = len(members)

    print(f"Searching for '{request}'")
    results = defaultdict(int)
    for member in enumerate(members):
        lyrics = songs.extractfile(member[1])

        lyrics = lyrics.read().decode("utf-8")
        match_count = len(pattern.findall(lyrics))

        #save count of all occurrences in list, use bisect to insert based on count
        print(f"{member[0]}/{member_count}", end="\r", flush=True)

        # if any matches
        if match_count > 0:
            name = member[1].name.rstrip(".txt")
            results[name] += match_count

    #sort list of matches by value
    results = list(results.items())
    top_100 = sorted(results, key=lambda x: x[1], reverse=True)
    top_100 = top_100[:100]

    #Save to results/
    timestamp = "{:%Y-%b-%d %H:%M:%S}".format(datetime.now())
    with open(f"{RESULTS}{request}_{timestamp}.csv", "w+") as save_to:
        writer = csv.writer(save_to, delimiter="|")
        for result in top_100:
            artist, song = result[0].split("_")
            match_count = result[1]
            row = [artist, song, str(match_count)]
            try:
                writer.writerow(row)
            except:
                continue

    print(f"\nSearch for '{request}' finished.")

    #TODO, make note of using quit... 
    #   try using break instead so that I get to see the other print statments
    #TODO, the lyrics themselves are not normalized, 
    #   so there may be many false negative matches
    #   using case-insensitive matching helps, but there's the issue of the punctuation

def sentence_list_search():
    """Basically, this block is supposed to be the same as a regular sentence sentence search,
        but placed within a for loop."""

    sentences = args.sentencelist.readlines()
    print("sentences:", sentences)

    #get memberlist
    print("Collecting archives...")
    songs = tarfile.open(ENG_TARBALL)
    members = songs.getmembers()
    member_count = len(members)

    #forloop this
    for sentence in sentences:
        sentence = sentence.strip()
        pattern = re.compile(sentence, re.IGNORECASE)

        print(f"Searching for '{sentence}'")
        results = defaultdict(int)
        for member in enumerate(members):
            lyrics = songs.extractfile(member[1])
            lyrics = lyrics.read().decode("utf-8")
            match_count = len(pattern.findall(lyrics))

            #save count of all occurrences in list, use bisect to insert based on count
            print(f"{member[0]}/{member_count}", end="\r", flush=True)

            # if any matches
            if match_count > 0:
                name = member[1].name.rstrip(".txt")
                results[name] += match_count
    
        #sort list of matches by value
        results = list(results.items())
        top_100 = sorted(results, key=lambda x: x[1], reverse=True)
        top_100 = top_100[:100]

        #Save to results/
        timestamp = "{:%Y-%b-%d %H:%M:%S}".format(datetime.now())
        with open(f"{RESULTS}{sentence}_{timestamp}.csv", "w+") as save_to:
            writer = csv.writer(save_to, delimiter="|")
            for result in top_100:
                artist, song = result[0].split("_")
                match_count = result[1]
                row = [artist, song, str(match_count)]
                try:
                    writer.writerow(row)
                except:
                    continue
        print(f"\nSearch for '{sentence}' finished.", end="\n", flush=True)
    songs.close()


def vocab_list_search():
    """Search for a list of vocabulary words."""
    print("Searching for vocab list.")
    #TODO, the scoring/ranking is off, can't have a score of 1500 but yet it does...

    #Load files
    words = args.vocablist.read()
    songs = tarfile.open(VOCAB_TARBALL)

    #get memberlist
    print("Collecting archives...")
    members = songs.getmembers()
    member_count = len(members)

    print(f"Searching for vocabulary...")
    results = defaultdict(int)
    for member in enumerate(members):
        lyrics = songs.extractfile(member[1])
        lyrics = lyrics.read().decode("utf-8")
        
        #search for each word, calculate match ratio
        match_count = 0
        for word in words:
            if word.strip() in lyrics:
                match_count += 1
        match_ratio = int((match_count/len(lyrics)) * 100)

        #save in dictionary
        name = member[1].name.rstrip(".txt")
        results[name] += match_ratio
        print(f"{member[0]}/{member_count}", end="\r", flush=True)

    #sort list of matches by value
    results = list(results.items())
    top_100 = sorted(results, key=lambda x: x[1], reverse=True)
    top_100 = top_100[:100]

    #Save to results/
    timestamp = "{:%Y-%b-%d %H:%M:%S}".format(datetime.now())
    save_to = f"{RESULTS}vocabulary_{timestamp}.csv"
    with open(save_to, "w+") as save_to:
        writer = csv.writer(save_to, delimiter="|")
        for result in top_100:
            artist, song = result[0].split("_")
            match_ratio = result[1]
            row = [artist, song, str(match_ratio)]
            try:
                writer.writerow(row)
            except:
                continue

    songs.close()
    print(f"\nFinished searching. Look in {save_to} for your results.")


if __name__ == "__main__":

    #Load description
    with open(SEARCH_DESC) as f:
        how_to_use = f.read()

    #Load epilog
    with open(SEARCH_EPILOG) as f:
        examples = f.read()

    parser = argparse.ArgumentParser(prog="Search" ,formatter_class=argparse.RawDescriptionHelpFormatter, description=how_to_use, epilog=examples)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--interactive", action="store_true", help="Run the search program interactively.")
    group.add_argument("--sentencelist", action="store", nargs="?", type=argparse.FileType("r"), metavar=("FILE"), help="Search for a list of specfic strings.")
    group.add_argument("--vocablist", action="store", nargs="?", type=argparse.FileType("r"), metavar=("FILE"), help="Search for a list of vocab words from FILE")

    group.add_argument("--cprofile", action="store_true", help="Run cProfile. Uncomment the code, then run.")

    args = parser.parse_args()

    if args.interactive:
        interactive_search()

    elif args.sentencelist:
        sentence_list_search()

    elif args.vocablist:
        vocab_list_search()

    elif args.cprofile:
        import cProfile
        print("Collecting archives...")
        songs = tarfile.open(ENG_TARBALL)
        members = songs.getmembers()
#         songs = tarfile.open(UNCOMPRESSED_TESTING)
        
#CPROFILE
#         print("Profiling...")
#         cProfile.run("artist_search(songs, members)", filename=f"profile_results/artist_search_{datetime.utcnow()}.stats")
#         cProfile.run("lyric_search(songs, members)", filename=f"profile_results/lyric_search_{datetime.utcnow()}.stats")
#         cProfile.run("song_search(songs, members)", filename=f"profile_results/song_search_{datetime.utcnow()}.stats"))
#         cProfile.run("regex_search(songs, members)", filename=f"profile_results/regex_search_{datetime.utcnow()}.stats"))
#         cProfile.run("sentence_search(songs, members)", filename=f"profile_results/sentence_search_{datetime.utcnow()}.stats"))

#LINE_PROFILER (kernprof)
print("Loading tarball...")
songs = tarfile.open(ENG_TARBALL)
members = songs.getmembers()
print("Profiling...")
artist_search(songs, members)
