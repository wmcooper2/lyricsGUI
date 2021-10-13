#std lib
import sqlite3
import tkinter as tk

#3rd party
import pytest

#custom
import db_util as db


#TODO: Class scoped DB connection


class TestLyricsDB:

    #TODO: replace with tempdir DB
#     @pytest.fixture
#     def db_connection(self, database, tempdir):
#         return sqlite3.Connection(tempdir)
#         return db.lyrics_db()

    @pytest.fixture
    def db_connection(self, database):
        return db.lyrics_db()

    @pytest.fixture
    def database(self):
        return "lyrics"

    @pytest.fixture
    def table(self):
        return "songs"

    def test_db_connection(self, db_connection):
        cur, con = db_connection
        assert isinstance(cur, sqlite3.Cursor)
        assert isinstance(con, sqlite3.Connection)
        db.close_connection(cur, con)

    def test_connect_to_database_with_name(self):
        cur, con = db.lyrics_db()
        assert isinstance(cur, sqlite3.Cursor)
        assert isinstance(con, sqlite3.Connection)
        db.close_connection(cur, con)

    def test_record_exists_in_db(self, db_connection, table):
        cur, con = db_connection
        assert db.record_check(table, "The Bellas", "Toxic", cur) is True

    def test_record_count_in_demo_db_unchanged(self, database, table):
        assert db.record_count(database, table) == 616312

    def test_get_song_name_from_exact_artist_query(self, database, table):
        result = db.artist(table, "The Bellas")
        assert result == ["Freedom! '90 x Cups", "I Don't Like It, I Love I", 'Toxic', 'Cake by the Ocean', 'Cheap Thrills']

    def test_get_records_from_exact_artist_query(self, database, table):
        result = db.artist2(table, "The Bellas")
        assert result == [('The Bellas', "Freedom! '90 x Cups"), ('The Bellas', "I Don't Like It, I Love I"), ('The Bellas', 'Toxic'), ('The Bellas', 'Cake by the Ocean'), ('The Bellas', 'Cheap Thrills')]

    def test_get_list_of_unique_artists(self, database, table):
        result = db.artists(table)
        assert len(result) == 66483

    def test_get_lyrics_with_artist_and_song_query(self, database, table):
        result = db.artist_and_song(table, "The Bellas", "Toxic")
        #NOTE: hacky workaround due to newline escaping issue in actual lyrics
        assert result[:10] == "Baby, can'"
        assert len(result) == 1387

    def test_get_100_records(self, database, table):
        result = db.index_search(database, table, 0, 99)
        assert len(result) == 100

    def test_get_all_songs_from_single_artist(self, database, table):
        result = db.song_query(database, table, "The Bellas")
        assert len(result) == 5

    def test_record_count_in_demo_db_unchanged(self, database, table):
        assert db.record_count(database, table) == 616312

    def test_get_songs_from_fuzzy_artist_query(self, database, table):
        result = db.fuzzy_artist(database, table, "the bellas")
        assert result == [('The Bellas', "Freedom! '90 x Cups"), ('The Bellas', "I Don't Like It, I Love I"), ('The Bellas', 'Toxic'), ('The Bellas', 'Cake by the Ocean'), ('The Bellas', 'Cheap Thrills')] 

    def test_get_lyrics_from_fuzzy_artist_and_song_query(self, database, table):
        result = db.fuzzy_artist_and_song(database, table, "the bellas", "toxic")
        assert result[:10] == "Baby, can'"
        assert len(result) == 1387

    def test_get_all_records_which_share_the_same_song_name_fuzzy_song_query(self, database, table):
        result = db.fuzzy_song(database, table, "Toxic")
        assert len(result) == 18 

    def test_get_artists_who_share_the_same_songs_name(self, database, table):
        result = db.artist_query(database, table, "Toxic")
        assert result == [('The Bellas', 'Toxic'), ('Hit Crew', 'Toxic'), ('Front Line Assembly', 'Toxic'), ('Countdown', 'Toxic'), ('David Donatien', 'Toxic'), ('Crazy Town', 'Toxic'), ('Britney Spears', 'Toxic'), ('A Static Lullaby', 'Toxic'), ('Alex & Sierra', 'Toxic'), ('Tristan Prettyman', 'Toxic'), ('Shoichiro Hirata', 'Toxic'), ('Soundalikes', 'Toxic'), ('The Starlite Singers', 'Toxic'), ('These Bones', 'Toxic'), ('Sarah Darling', 'Toxic'), ('Souls', 'Toxic'), ('Robbie Williams', 'Toxic'), ('Local H', 'Toxic')]

    #add record to DB
    #delete record from DB
    #update record in DB



