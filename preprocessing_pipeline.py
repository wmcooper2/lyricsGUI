"""Pipeline for extracting lyrics file from tarfile and normalizing text for use in the next stage of the ML process.
"""

from pprint import pprint
import re
import tarfile

from file_util import remove_all_punct


tar = tarfile.open("lyrics.tar.gz", "r:gz")
names = tar.getnames()
lyrics = tar.extractfile("Volumes/WHITE1000/DATA/LYRICS/lyrics in sets/lyrics/block99/Kataklysm_Face the Face of War.txt")
file_name = names[1000]
s = tar.extractfile(file_name).read()
# print(s)

# treat newlines as periods and replace them
no_newlines = re.sub("\\r\\n", ".", s.decode("utf-8"))
# print("no_newlines:", no_newlines)

# replace ellipses with zero-length string
no_ellipses = re.sub("\.\.\.", "", no_newlines)
# print("no_ellipses:", no_ellipses)

# replace double periods with single period
no_double_periods = re.sub("\.\.", ".", no_ellipses)
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

# remove the double spaces introduced earlier in the pipeline
double_space = re.compile("  ")
no_double_space = double_space.sub(" ", no_punct)
# print("no double space:", no_double_space)

# remove the extra s created from removing the apostrophies
isolated_s = re.compile(" s ")
no_isolated_s = isolated_s.sub(" ", no_double_space)
# print("no isolated s'es:", no_isolated_s)

# convert the isolated t created from removing the apostrophies to "not"
isolated_t = re.compile("n t ")
no_isolated_t = isolated_t.sub(" not ", no_isolated_s)
print("no isolated t's:", no_isolated_t)


#TODO: check all normalized words at this point against a real dictionary to find out what words are valid
#TODO: filter out the non-English words
