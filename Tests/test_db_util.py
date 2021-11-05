#std lib
import sqlite3
import tkinter as tk

#3rd party
import pytest

#custom
from database import Database, FuzzyDatabase


#TODO: Class scoped DB connection


class TestLyricsDB:

    #TODO: replace with tempdir DB
#     @pytest.fixture
#     def db_connection(self, database, tempdir):
#         return sqlite3.Connection(tempdir)
#         return db.lyrics_db()

#     @pytest.fixture
#     def db_connection(self, database):
#         return db.

    @pytest.fixture(scope="module")
    def database(self):
        return Database()

    @pytest.fixture(scope="module")
    def fuzzy_database(self):
        return FuzzyDatabase()

#     @pytest.fixture(scope="module")
#     def cursor(database):
#         return database.connection.cursor()

    def test_db_connection(self, database):
        con, cur = database.con_cur()
        assert isinstance(cur, sqlite3.Cursor)
        assert isinstance(con, sqlite3.Connection)
#         db.close_connection(cur, con)

#     def test_connect_to_database_with_name(self):
#         cur, con = db.lyrics_db()
#         assert isinstance(cur, sqlite3.Cursor)
#         assert isinstance(con, sqlite3.Connection)
# #         db.close_connection(cur, con)

    def test_record_exists_in_db(self, database):
        con, cur = database.con_cur()
        assert database.record_check("The Police", "Roxanne", cur) is True

    def test_record_count_in_demo_db_unchanged(self, database):
        #TODO, add db fixture
#         cur = database.connection.cursor()
        assert database.record_count() == 616312

    #testing get songs from artist
#     def test_get_song_name_from_exact_artist_query(self):
#         result = db.artist(table, "The Bellas")
#         assert result == ["Freedom! '90 x Cups", "I Don't Like It, I Love I", 'Toxic', 'Cake by the Ocean', 'Cheap Thrills']

    def test_get_list_of_unique_artists(self, database):
        result = database.artists()
        assert len(result) == 66483

    def test_get_lyrics_with_artist_and_song_query(self, database):
        result = database.artist_and_song("The Police", "Roxanne")
        assert result.artist == "The Police"
        assert result.song == "Roxanne"

    def test_get_100_records(self, database):
        result = database.index_search(0, 99)
        assert len(result) == 100

    def test_get_all_songs_from_single_artist(self, database):
        result = database.songs_from_artist("The Police")
        assert len(result) == 134

    def test_get_songs_from_fuzzy_artist_query(self, fuzzy_database):
        result = fuzzy_database.fuzzy_songs_from_artist("the police")
        assert len(result) == 352

    def test_get_lyrics_from_fuzzy_artist_and_song_query(self, fuzzy_database):
        result = fuzzy_database.fuzzy_artist_and_song("the police", "roxanne")
        assert result.artist == "The Police"
        assert result.song == "Roxanne"

    def test_get_all_records_which_share_the_same_song_name_fuzzy_song_query(self, fuzzy_database):
        result = fuzzy_database.fuzzy_song("roxanne")
        assert len(result) == 5

#     def test_get_artists_who_share_the_same_songs_name(self):
#         result = db.artist_query("Toxic")
#         assert result == [('The Bellas', 'Toxic'), ('Hit Crew', 'Toxic'), ('Front Line Assembly', 'Toxic'), ('Countdown', 'Toxic'), ('David Donatien', 'Toxic'), ('Crazy Town', 'Toxic'), ('Britney Spears', 'Toxic'), ('A Static Lullaby', 'Toxic'), ('Alex & Sierra', 'Toxic'), ('Tristan Prettyman', 'Toxic'), ('Shoichiro Hirata', 'Toxic'), ('Soundalikes', 'Toxic'), ('The Starlite Singers', 'Toxic'), ('These Bones', 'Toxic'), ('Sarah Darling', 'Toxic'), ('Souls', 'Toxic'), ('Robbie Williams', 'Toxic'), ('Local H', 'Toxic')]

    #add record to DB
    #delete record from DB
    #update record in DB



    def test_all_records_returns_generator(self, database):
        #hacky workaround for not using a generator class type
        generator = database.all_records()
        assert hasattr(generator, "__next__")
        assert hasattr(generator, "__iter__")
