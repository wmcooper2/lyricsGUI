#std lib
from collections import namedtuple
import sqlite3
import tkinter as tk

#3rd party
import pytest

#custom
import search


@pytest.fixture(scope="module")
def Search():
    root = tk.Tk()
    frame = tk.Frame(root)
    return search.Search(frame)

@pytest.fixture(scope="module")
def Query():
    Query = namedtuple("Query", ["artist", "song", "grammar"])
    return Query

@pytest.fixture(scope="module")
def all_three(Query):
    return Query("The Police", "Roxanne", "red light")

@pytest.fixture(scope="module")
def bad_entry():
    return "lkjei"



class TestExactObjectCreation:
    """Test that the fundamental objects for this module are created."""

    def test_create_search_object(self, Search):
        assert Search

    def test_create_query(self, all_three):
        q = all_three
        assert q
        assert q.artist == "The Police"
        assert q.song ==  "Roxanne"
        assert q.grammar == "red light"

    @pytest.mark.xfail
    def test_create_query_defaults_fails(self, Query):
        q = Query()
        assert q


class TestExactArtistSongGrammar:
    """Test entry pattern Artist-Song-Grammar."""

    def test_search_artist_song_grammar_returns_2_tuple_result(self, Search, all_three):
        q = all_three
        result, lyrics = Search.exact_all_three(q)
        assert len(result) == 2
        assert isinstance(result, tuple)

    def test_search_artist_song_grammar_result_is_Display_Record(self, Search, all_three):
        q = all_three
        result = Search.exact_all_three(q)[0]
        assert isinstance(result, search.DisplayRecord)

    def test_search_artist_song_grammar_returns_empty_record_on_bad_artist(self, Search, Query, bad_entry):
        q = Query(bad_entry, "Roxanne", "red light")
        result, lyrics = Search.exact_all_three(q)
        assert len(result) == 2
        assert isinstance(result, tuple)
        assert result.artist == ""
        assert result.song == ""
        assert lyrics == None

    def test_search_artist_song_grammar_returns_empty_record_on_bad_song(self, Search, Query, bad_entry):
        q = Query("The Police", bad_entry, "red light")
        result, lyrics = Search.exact_all_three(q)
        assert len(result) == 2
        assert isinstance(result, tuple)
        assert result.artist == ""
        assert result.song == ""
        assert lyrics == None

    def test_search_artist_song_grammar_returns_empty_record_on_bad_grammar(self, Search, Query, bad_entry):
        q = Query("The Police", "Roxanne", bad_entry)
        result, lyrics = Search.exact_all_three(q)
        assert len(result) == 2
        assert isinstance(result, tuple)
        assert result.artist == ""
        assert result.song == ""
        assert lyrics == None


class TestExactArtistSong:
    """Test entry pattern Artist-Song-None."""

    def test_search_artist_song_returns_2_tuple_result(self, Search, Query):
        q = Query("The Police", "Roxanne", "")
        result, lyrics = Search.exact_artist_song(q)
        assert len(result) == 2
        assert isinstance(result, tuple)

    def test_search_artist_song_result_is_Display_Record(self, Search, Query):
        q = Query("The Police", "Roxanne", "")
        result = Search.exact_artist_song(q)[0]
        assert isinstance(result, search.DisplayRecord)

    def test_search_artist_song_returns_2_list_result(self, Search, Query):
        q = Query("The Police", "Roxanne", "")
        result, lyrics = Search.exact_artist_grammar(q)
        record = result[0]
        assert len(result) == 134
        assert isinstance(record, search.DisplayRecord)

    def test_search_artist_song_result_is_Display_Record(self, Search, Query):
        q = Query("The Police", "Roxanne", "")
        result, lyrics = Search.exact_artist_grammar(q)
        assert isinstance(result[0], search.DisplayRecord)
        assert lyrics is None

    def test_search_artist_song_returns_empty_record_on_bad_artist(self, Search, Query, bad_entry):
        q = Query(bad_entry, "Roxanne", "red light")
        result, lyrics = Search.exact_artist_song(q)
        assert len(result) == 2
        assert isinstance(result, tuple)
        assert result.artist == ""
        assert result.song == ""
        assert lyrics == ""

    def test_search_artist_song_returns_empty_record_on_bad_song(self, Search, Query, bad_entry):
        q = Query("The Police", bad_entry, "red light")
        result, lyrics = Search.exact_artist_song(q)
        assert len(result) == 2
        assert isinstance(result, tuple)
        assert result.artist == ""
        assert result.song == ""
        assert lyrics == ""


class TestExactArtistGrammar:
    """Test entry pattern Artist-None-Grammar."""

    def test_search_artist_grammar_result_is_Display_Record(self, Search, all_three):
        result, lyrics = Search.exact_artist_grammar(all_three)
        record = result[0]
        assert isinstance(record, search.DisplayRecord)

    def test_search_artist_grammar_returns_2_list_result(self, Search, all_three):
        result, lyrics = Search.exact_artist_grammar(all_three)
        record = result[0]
        assert len(result) == 6
        assert isinstance(record, search.DisplayRecord)

    def test_search_artist_grammar_returns_empty_record_on_bad_artist(self, Search, Query, bad_entry):
        q = Query(bad_entry, "Roxanne", "red light")
        result, lyrics = Search.exact_artist_grammar(q)
        record = result[0]
        assert len(result) == 1
        assert isinstance(record, search.DisplayRecord)
        assert record.artist == ""
        assert record.song == ""
        assert lyrics == None

    def test_search_artist_song_grammar_returns_empty_record_on_bad_grammar(self, Search, Query, bad_entry):
        q = Query("The Police", "Roxanne", bad_entry)
        result, lyrics = Search.exact_artist_grammar(q)
        record = result[0]
        assert len(result) == 1
        assert isinstance(record, search.DisplayRecord)
        assert record.artist == ""
        assert record.song == ""
        assert lyrics == None


class TestExactSongGrammar:
    """Test entry pattern None-Song-Grammar."""

    def test_search_song_grammar_result_is_Display_Record(self, Search, all_three):
        result, lyrics = Search.exact_artist_grammar(all_three)
        record = result[0]
        assert isinstance(record, search.DisplayRecord)

    def test_search_song_grammar_returns_2_list_result(self, Search, all_three):
        result, lyrics = Search.exact_artist_grammar(all_three)
        record = result[0]
        assert len(result) == 6
        assert isinstance(record, search.DisplayRecord)

    def test_search_song_grammar_returns_empty_record_on_bad_song(self, Search, Query, bad_entry):
        q = Query("The Police", bad_entry, "red light")
        result, lyrics = Search.exact_song_grammar(q)
        record = result[0]
        assert len(result) == 1
        assert isinstance(record, search.DisplayRecord)
        assert record.artist == ""
        assert record.song == ""
        assert lyrics == None

    def test_search_song_grammar_returns_empty_record_on_bad_grammar(self, Search, Query, bad_entry):
        q = Query("The Police", "Roxanne", bad_entry)
        result, lyrics = Search.exact_song_grammar(q)
        record = result[0]
        assert len(result) == 1
        assert isinstance(record, search.DisplayRecord)
        assert record.artist == ""
        assert record.song == ""
        assert lyrics == None


@pytest.mark.skip
class TestExactGrammar:
    """Test entry pattern None-None-Grammar."""

    def test_search_grammar_result_is_Display_Record(self, Search, all_three):
        #TODO: mock Search.clear_lyrics() because it calls the same method in its master
        result, lyrics = Search.exact_grammar(all_three)
        record = result[0]
        assert isinstance(record, search.DisplayRecord)



class TestExactSong:
    """Test entry pattern None-Song-None"""

    def test_search_song_result_is_Display_Record(self, Search, all_three):
        result, lyrics = Search.exact_song(all_three)
        record = result[0]
        assert isinstance(record, search.DisplayRecord)

    def test_search_artist_grammar_returns_2_list_result(self, Search, all_three):
        result, lyrics = Search.exact_song(all_three)
        record = result[0]
        assert len(result) == 5
        assert isinstance(record, search.DisplayRecord)

    def test_search_song_result_is_empty_record_on_bad_song(self, Search, Query, bad_entry):
        q = Query("The Police", bad_entry, "red light")
        result, lyrics = Search.exact_song(q)
        record = result[0]
        assert len(result) == 1
        assert isinstance(record, search.DisplayRecord)
        assert record.artist == ""
        assert record.song == ""
        assert lyrics == None


class TestExactArtist:
    """Test entry pattern Artist-None-None"""

    def test_search_artist_result_is_Display_Record(self, Search, all_three):
        result, lyrics = Search.exact_song(all_three)
        record = result[0]
        assert isinstance(record, search.DisplayRecord)

    def test_search_artist_returns_2_list_result(self, Search, all_three):
        result, lyrics = Search.exact_artist(all_three)
        record = result[0]
        assert len(result) == 134
        assert isinstance(record, search.DisplayRecord)

    def test_search_artist_result_is_empty_record_on_bad_artist(self, Search, Query, bad_entry):
        q = Query(bad_entry, "Roxanne", "red light")
        result, lyrics = Search.exact_artist(q)
        record = result[0]
        assert len(result) == 1
        assert isinstance(record, search.DisplayRecord)
        assert record.artist == ""
        assert record.song == ""
        assert lyrics == None


