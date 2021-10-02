#std lib
import tkinter as tk

#3rd party
import pytest

#custom
import db_util as db
from lyricstab import LyricsTab

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

    
    


@pytest.fixture
def App():
    return LyricsTab(tk.Tk())

@pytest.fixture
def lyrics():
    return db.artist_and_song(Data.demo_artist_exact, Data.demo_song_exact)



def test_lyrics(lyrics):
    assert lyrics[:10] == Data.demo_lyrics_snippet
    assert len(lyrics) == Data.demo_lyrics_len


#TODO
def test_gap_search(App, lyrics):
    assert App.distant_neighboring_words(lyrics, ["need", "a"], 1) == str(True)

