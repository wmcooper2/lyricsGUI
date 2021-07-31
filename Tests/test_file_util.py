# std lib
import tarfile
import types


# custom
from constants import TARS
from file_util import (
    all_songs_artists_and_names,
    extract_file_contents_as_list,
    split_name,
    Song,
    tar_contents,
    word_list)


words = word_list("/usr/share/dict/web2")
compressed_tarball = f"{TARS}testing_compressed.tar.gz"
uncompressed_tarball = f"{TARS}testing_uncompressed.tar"


def test_word_list_returns_list():
    assert type(words) == list


def test_word_list_returns_not_empty():
    assert len(words) > 0


def test_word_list_elements_are_strings():
    assert all(map(lambda x: type(x) == str, words)) == True


def test_tar_contents_returns_generator():
    assert type(tar_contents(compressed_tarball)) == types.GeneratorType


def test_split_name_returns_list():
    string = "someblock100/someartist_some song.txt"
    assert type(split_name(string)) == list
    assert len(split_name(string)) == 2


def test_split_name_has_no_txt_string():
    """The .txt suffix has been removed from the file name."""
    string = "someblock100/someartist_some song.txt"
    assert ".txt" not in split_name(string)[-1]


def test_get_file_info_returns_list_of_song_tuples():
    results = all_songs_artists_and_names(uncompressed_tarball)
    assert type(results) == list
#     assert type(results[1]) == tuple


def test_extract_file_contents_as_list_from_uncompressed_tarball():
    song = "Rihanna_Consideration.txt"
    result = extract_file_contents_as_list(song, uncompressed_tarball)
    assert type(result) == list
    assert type(result[0]) == str


def test_extract_file_contents_as_list_from_compressed_tarball():
    song = "Rihanna_Consideration.txt"
    result = extract_file_contents_as_list(song, compressed_tarball)
    assert type(result) == list
    assert type(result[0]) == str


#TODO
# def test_divide_tarball(tmpdir):
#     pass
    
