# std lib
from string import ascii_lowercase
from tarfile import TarInfo
from types import GeneratorType

# custom
from constants import TARS
from metrics_util import (
    calculate_english_score,
    load_songs,
    normalize_words,
    save_word_list,
    word_set,
    words_in_dict)
from scrapeutil import load_file_list

#Example of using tempdirs in pytest
#test, loading local dict, bad word list, scoring function
# CONTENT = "content"
# def test_create_file(tmp_path):
#     d = tmp_path / "sub"
#     d.mkdir()
#     p = d / "hello.txt"
#     p.write_text(CONTENT)
#     assert p.read_text() == CONTENT
#     assert len(list(tmp_path.iterdir())) == 1

dictionary = "/usr/share/dict/web2"
ref_dict = set(load_file_list(dictionary))
uncompressed_tarfile = f"{TARS}testing_uncompressed.tar"
compressed_tarfile = f"{TARS}testing_compressed.tar.gz"


def test_save_word_list(tmpdir):
    temp_file = tmpdir / "tempfile.txt"
    save_word_list(temp_file, set(["cats", "birds"]))
    with open(temp_file, "r") as f:
        data = f.readlines()
    
    #Have to test for membership because order is not guaranteed with simple sets
    assert "cats\n" in data
    assert "birds\n" in data
#     assert data == ['cats\n', 'birds\n']
        

def test_word_set_is_set():
    assert type(word_set(dictionary)) == set


def test_word_set_all_lowercase():
    assert all([word[0] in ascii_lowercase for word in word_set(dictionary)])


def test_words_in_dict():
    list_ = ["Cat", "Banana", "kjidkj", "lklkj"]
    dict_ = set(load_file_list(dictionary))
    found, not_found = words_in_dict(list_, dict_)
    assert len(found) == 2
    assert len(not_found) == 2


def test_normalize_words():
    list_ = ["Cat$", "President:cheese", "Banana!", "what's", ""]
    assert normalize_words(list_) == ["cat", "presidentcheese", "banana", "whats"]


def test_calculate_english_score():
    bad_lyrics = "This is an English line. This is gibbirish lkjlkjs lkj jioew jkeieie jksal."
    no_lyrics = ""
    assert calculate_english_score(bad_lyrics, ref_dict) == 36 
    assert calculate_english_score(no_lyrics, ref_dict) == 0


def test_load_songs_returns_generator():
    assert type(load_songs(compressed_tarfile)) == GeneratorType


def test_load_uncompressed_tarball_returns_generator():
    assert type(load_songs(uncompressed_tarfile)) == GeneratorType

