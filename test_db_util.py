#std lib
import sqlite3
import tkinter as tk

#3rd party
import pytest

#custom
import db_util as db


class Data:
    #the full database
    lyrics_db_path = "Databases/lyrics.db"
    songs_table = "songs"
    lyrics_record_count = 616312

    #demo database
    demo_db_path = "Databases/demo.db"
    demo_table = "demo"
    demo_artist_exact = "The Bellas"
    demo_artist_fuzzy = "the bellas"
    demo_song_exact = "Toxic"
    demo_song_fuzzy = "toxic"
    demo_lyrics_snippet = "Baby, can'"
    demo_lyrics_len = 1387
    demo_db_unique_artists_count = 6930
    demo_artist_and_songs = [('The Bellas', "Freedom! '90 x Cups"), ('The Bellas', "I Don't Like It, I Love I"), ('The Bellas', 'Toxic')]
    demo_record_count = 60000
    index_start = 0
    index_step = 99
    shared_song_names = [('The Bellas', 'Toxic'), ('Hit Crew', 'Toxic')]



class TestDemoDB:

    @pytest.fixture
    def db_connection(self):
        return db.connect()

    def test_db_connection(self, db_connection):
        cur, con = db_connection
        assert isinstance(cur, sqlite3.Cursor)
        assert isinstance(con, sqlite3.Connection)
        db.close_connection(cur, con)

    def test_get_song_name_from_exact_artist_query(self):
        result = db.artist(Data.demo_artist_exact)
        assert result == ["Freedom! '90 x Cups", "I Don't Like It, I Love I", 'Toxic']

    def test_get_records_from_exact_artist_query(self):
        result = db.artist2(Data.demo_artist_exact)
        assert result == Data.demo_artist_and_songs

    def test_get_list_of_unique_artists(self):
        result = db.artists()
        assert len(result) == Data.demo_db_unique_artists_count

    def test_get_lyrics_with_artist_and_song_query(self):
        result = db.artist_and_song(Data.demo_artist_exact, Data.demo_song_exact)
        #NOTE: hacky workaround due to newline escaping issue in actual lyrics
        assert result[:10] == Data.demo_lyrics_snippet
        assert len(result) == Data.demo_lyrics_len

    def test_get_100_records(self):
        result = db.index_search(Data.index_start, Data.index_step)
        assert len(result) == 100

    def test_get_songs_from_fuzzy_artist_query(self):
        result = db.fuzzy_artist(Data.demo_artist_fuzzy)
        assert result == Data.demo_artist_and_songs

    def test_get_lyrics_from_fuzzy_artist_and_song_query(self):
        result = db.fuzzy_artist_and_song(Data.demo_artist_fuzzy, Data.demo_song_fuzzy)
        assert result[:10] == Data.demo_lyrics_snippet
        assert len(result) == Data.demo_lyrics_len

    def test_get_all_records_which_share_the_same_song_name_fuzzy_song_query(self):
        result = db.fuzzy_song(Data.demo_song_exact)
        assert len(result) == 2

    def test_record_count_in_demo_db_unchanged(self):
        assert db.record_count() == Data.demo_record_count

    def test_get_artists_who_share_the_same_songs_name(self):
        result = db.artist_query(Data.demo_song_exact)
        assert result == Data.shared_song_names

    def test_get_all_songs_from_single_artist(self):
        result = db.song_query(Data.demo_artist_exact)
        assert len(result) == 3

    #add record to DB
    #delete record from DB
    #update record in DB



class TestLyricsDB:

    @pytest.fixture
    def db_connection(self):
        return db.connect_to(Data.lyrics_db_path)

    def test_connect_to_database_with_name(self):
        cur, con = db.connect_to(Data.lyrics_db_path)
        assert isinstance(cur, sqlite3.Cursor)
        assert isinstance(con, sqlite3.Connection)
        db.close_connection(cur, con)

    def test_record_exists_in_db(self, db_connection):
        cur, con = db_connection
        assert db.record_check(Data.demo_artist_exact, Data.demo_song_exact, cur) is True

    def test_record_count_in_demo_db_unchanged(self):
        assert db.record_count(Data.songs_table) == Data.lyrics_record_count

