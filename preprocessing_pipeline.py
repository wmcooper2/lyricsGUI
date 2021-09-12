"""Pipeline for extracting lyrics file from tarfile and normalizing text for use in the next stage of the ML process.
"""

# std lib
import pickle
from pprint import pprint
import re
import tarfile

# custom
from file_util import remove_all_punct
from metrics_util import word_set, english_score, words_in_dict
from trie import Trie
from scrape_util import progress_bar

#================================================================================
#   processing a single song's lyrics 
#================================================================================
def pipeline(file_name):
    # Work on a single song for testing
#     file_name = names[1000]
    try:
        s = tar.extractfile(file_name).read()
    except AttributeError:
        # likely a NoneType due to the dir name being read in from the tarfile
        return None
    if DEBUG: print(f"Extracted contents of '{file_name}'.")

    # treat newlines as periods and replace them
    no_newlines = re.sub("\\r\\n", ".", s.decode("utf-8"))
    if DEBUG: print(f"no_newlines:\n {no_newlines}\n")

    # replace ellipses with zero-length string
    no_ellipses = re.sub("\.\.\.", "", no_newlines)
    if DEBUG: print(f"no_ellipses:\n {no_ellipses}\n")

    # replace double periods with single period
    no_double_periods = re.sub("\.\.", ".", no_ellipses)
    if DEBUG: print(f"no_double_periods:\n {no_double_periods}\n")

    #TODO: list lines 
    # split into lines at the periods
    # pprint(no_double_periods.split("."))

    #TODO: expand the appropriate apostrophies

    # make all letters lowercase
    lowercase = no_double_periods.lower()

    # remove all punctuation
    punct = re.compile("[!\"#$%&\'()*+,-./:;<=>?@\\[\\]^_`{|}~]")
    no_punct = punct.sub(" ", lowercase)
    if DEBUG: print(f"no_punct:\n {no_punct}\n")

    # remove the double spaces introduced earlier in the pipeline
    double_space = re.compile("  ")
    no_double_space = double_space.sub(" ", no_punct)
    if DEBUG: print(f"no_double_space:\n {no_double_space}\n")

    # remove the extra s created from removing the apostrophies
    isolated_s = re.compile(" s ")
    no_isolated_s = isolated_s.sub(" ", no_double_space)
    if DEBUG: print(f"no_isolated_s:\n {no_isolated_s}\n")

    # convert the isolated t created from removing the apostrophies to "not"
    isolated_t = re.compile("n t ")
    no_isolated_t = isolated_t.sub(" not ", no_isolated_s)
    if DEBUG: print(f"no_isolated_t:\n {no_isolated_t}\n")

    # filter out the non-English words
    lyrics_set = set(no_isolated_t.split())
    valid_words = words_in_dict(lyrics_set, dictionary)
    if DEBUG: print(f"valid_words:\n {valid_words}")
    if DEBUG:
        word_count = len(lyrics_set)
        valid_count = len(valid_words)
        print(f"word_count: {word_count}, valid_count: {valid_count}, {round((valid_count/word_count)*100, 4)}%\n")

    # show the words not found in the dictionary
    # invalid_words = lyrics_set.difference(valid_words)
    # if DEBUG: print("invalid_words:\n", invalid_words)

    # update the main set
    main_set.update(valid_words)

# score = english_score(song, ref_dict)

# make trie of words
# t = Trie()
# for word in valid_words:
#         t.insert(word)
# if DEBUG: print("Trie created.")



#================================================================================
#   Main
#================================================================================
if __name__ == "__main__":
    DEBUG = False

    # load the built in dictionary
    dictionary_name = "/usr/share/dict/web2"
    dictionary = word_set(dictionary_name)
    if DEBUG: print(f"Loaded reference dictionary: '{dictionary_name}'")

    # load all the lyrics from a tar file
    lyrics_tar = "lyrics.tar.gz"
    tar = tarfile.open(lyrics_tar, "r:gz")
    if DEBUG: print(f"Loaded main tarfile '{lyrics_tar}'")

    # get list of entries in the tar
    names = tar.getnames()
    if DEBUG: print(f"Loaded name list.")

    # main set for all song lyrics
    main_set = set()

    # set counters for progress bar
    total_songs = len(names)
    songs_processed = 0

    for name in names:
        pipeline(name)

        # update progress bar
        songs_processed += 1
        progress_bar(songs_processed, total_songs)
    print("\nCompleted")


    #================================================================================
    #   pickling
    #================================================================================
    #616308 songs?
    save_to = open("main_set.pickle", "wb+")
    pickle.dump(main_set, save_to)
    save_to.close()






