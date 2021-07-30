# std lib
from collections import namedtuple
import re
import tarfile
from typing import Generator, List, Set, TypeVar

# 3rd party
# from nltk.stem.porter import *
from nltk.stem.porter import PorterStemmer

# custom
from file_util import (
    remove_all_punct,
    remove_all_digits,
    remove_all_empty_elements,
    tar_contents,
    word_list)


tarData = TypeVar("tar", tarfile.TarFile, None)
match = TypeVar("match", re.match, None)
Song = namedtuple("Song", ["artist", "name", "filePath"])

stemmer = PorterStemmer()


def calculate_english_score(lyrics: str, ref_dict: Set[str]) -> int:
    """Calculate a score based on how many English words were found."""
    try:
        normalized = normalize_words(lyrics.split())
        found, not_found = words_in_dict(normalized, ref_dict)  # sets
        amt_found = len(found)
        amt_not_found = len(not_found)
        score = round(amt_found / (amt_found + amt_not_found), 2)
    except ZeroDivisionError:
        return 0
    return int(score * 100)


def edit_distance(s1: str, s2: str) -> int:
    """Calculate edit distance between s1 and s2.
        Taken from https://stackoverflow.com/questions/2460177/edit-distance-in-python
    """

    if len(s1) > len(s2):
        s1, s2 = s2, s1
    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def load_songs2(name: tarData) -> Generator[List[str], None, None]:
    """Create generator of songs and file names."""
    files = tar_contents(name)
    with tarfile.open(name, "r", ignore_zeros=True) as tar:
        for file_ in files:
            # dirs in archive returned as None
            extracted = tar.extractfile(file_)
            if extracted is None:
                continue
            else: 
                result = extracted.read().decode("utf-8")
                yield result, file_.name  # gen, TarInfo.name


def load_songs(name: tarData) -> [Generator[List[str], None, None], str]:
    """Create generator of songs and file names."""
    files = tar_contents(name)
    with tarfile.open(name, "r", ignore_zeros=True) as tar:
        for file_ in files:
            # dirs in archive returned as None
            extracted = tar.extractfile(file_)
            if extracted is None:
                continue
            else: 
                result = extracted.read().decode("utf-8")
                yield result, file_.name  # gen, TarInfo.name


def load_uncompressed_tarball(name: tarData) -> [Generator[List[str], None, None], str]:
    """Create generator of songs and file names."""
    files = tar_contents(name)
    try:
        with tarfile.open(name, "r") as tar:
            for file_ in files:
                # dirs in archive returned as None
                extracted = tar.extractfile(file_)
                if extracted is None:
                    continue
                else: 
                    result = extracted.read().decode("utf-8")
                    yield result, file_.name  # gen, TarInfo.name
    except tarfile.ReadError:
        return None


def normalize_words(words: List[str]) -> List[str]:
    """Normalize all the words."""
    strip = (word.strip() for word in words)
    lower = (word.lower() for word in list(strip))
    no_punct = list(map(remove_all_punct, lower))
    no_digits = list(map(remove_all_digits, no_punct))
    return remove_all_empty_elements(no_digits)


def save_word_list(file_: str, words: Set[str]) -> None:
    """Save word list as text file."""
    with open(file_, "w+") as f:
        for word in words:
            f.write(f"{word}\n")


def word_set(dict_: str) -> Set[str]:
    """Return a normalized set of words from the 'dict_'."""
    dict_ = word_list(dict_)
    dict_ = [word.lower().strip() for word in dict_]
    return set(dict_)


def words_in_dict(list_: Set[str], dict_: Set[str]) -> [Set[str], Set[str]]:
    """Determine which words from list_ are in dict_."""
    not_found = set()
    found = set()
    for word in list_:
        if word in dict_:
            found.add(word) 
        else:
            not_found.add(word)
    #Try to find stemmed words not found in first pass
    for word in not_found.copy():
        stemmed = stemmer.stem(word)
        if stemmed in dict_:
            found.add(word)
            not_found.remove(word)
    return found, not_found
