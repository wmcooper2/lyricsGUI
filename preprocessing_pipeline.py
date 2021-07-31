"""Pipeline for extracting lyrics file from tarfile and normalizing text for use in the next stage of the ML process.
"""

# std lib
from pprint import pprint
import re
import tarfile

# custom
from file_util import remove_all_punct
from metrics_util import word_set, english_score, words_in_dict

DEBUG = True


# load the built in dictionary
dictionary_name = "/usr/share/dict/web2"
dictionary = word_set(dictionary_name)
if DEBUG: print(f"Loaded reference dictionary: '{dictionary_name}'")

# Work on a single song for testing
lyrics_tar = "lyrics.tar.gz"
tar = tarfile.open(lyrics_tar, "r:gz")
if DEBUG: print(f"Loaded main tarfile '{lyrics_tar}'")

names = tar.getnames()
if DEBUG: print(f"Loaded name list.")
# lyrics = tar.extractfile("Volumes/WHITE1000/DATA/LYRICS/lyrics in sets/lyrics/block99/Kataklysm_Face the Face of War.txt")
file_name = names[1000]
s = tar.extractfile(file_name).read()
if DEBUG: print(f"Extracted contents of '{file_name}'.")

# print(s)

# treat newlines as periods and replace them
no_newlines = re.sub("\\r\\n", ".", s.decode("utf-8"))
if DEBUG: print(f"no_newlines:\n {no_newlines}\n")
# print("no_newlines:", no_newlines)

# replace ellipses with zero-length string
no_ellipses = re.sub("\.\.\.", "", no_newlines)
if DEBUG: print(f"no_ellipses:\n {no_ellipses}\n")
# print("no_ellipses:", no_ellipses)

# replace double periods with single period
no_double_periods = re.sub("\.\.", ".", no_ellipses)
if DEBUG: print(f"no_double_periods:\n {no_double_periods}\n")
# print("no_double_periods:", no_double_periods)

### list lines 
# split into lines at the periods
# pprint(no_double_periods.split("."))




#need to 
# expand the appropriate apostrophies

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
# print("no double space:", no_double_space)

# remove the extra s created from removing the apostrophies
isolated_s = re.compile(" s ")
no_isolated_s = isolated_s.sub(" ", no_double_space)
if DEBUG: print(f"no_isolated_s:\n {no_isolated_s}\n")
# print("no isolated s'es:", no_isolated_s)

# convert the isolated t created from removing the apostrophies to "not"
isolated_t = re.compile("n t ")
no_isolated_t = isolated_t.sub(" not ", no_isolated_s)
if DEBUG: print(f"no_isolated_t:\n {no_isolated_t}\n")
print("no isolated t's:", no_isolated_t)


#TODO: check all normalized words at this point against a real dictionary to find out what words are valid
# show set of words found in dictionary
lyrics_set = set(no_isolated_t.split())
valid_words = words_in_dict(lyrics_set, dictionary)
if DEBUG: print(f"valid_words:\n {valid_words}\n")
if DEBUG:
    word_count = len(lyrics_set)
    valid_count = len(valid_words)
    print(f"word_count: {word_count}, valid_count: {valid_count}, {round((valid_count/word_count), 4) * 100}%")
# show set of words not found in dictionary



#TODO: calculate score of how many words found in dictionary
# score = english_score(song, ref_dict)
#TODO: filter out the non-English words
#TODO: look in metrics_util.py for functions that filter out non english words
