#std lib
from pathlib import Path
import tkinter as tk

# custom
from db_util import *


def count_files(dir_: str) -> None:
    """Count all files in dir_."""
    count_btn["text"] = "Counting..."
    for index, file_ in enumerate(Path(dir_).iterdir()):
        if file_.is_file():
            file_amt["text"] = str(index)
            root.update()
    count_btn["text"] = "Count Files"
    root.update()


def search() -> None:
    """Perform database query."""
    a = artist_search_entry.get().strip()
    s = song_search_entry.get().strip()
    w = word_phrase_entry.get().strip()

#     if a and s and w:
    if w and not s and not a:
        #perform regex search on lyrics column
#         word_phrase_search(w)
        print("still working on this...")

    elif a and s:
        result = artist_and_song(a, s)

        if result:
            #if found, show lyrics for that song from that artist
            lyrics_textbox.delete("1.0", tk.END)
            lyrics_textbox.insert("1.0", result)

    elif a:
        #only artist, if found, show song names
        songs = artist(a)
        list_results.delete(0, tk.END)
        amt = 0
        for index, song in enumerate(sorted(songs, reverse=True)):
            list_results.insert(0, song)
            amt = index
        search_results_frame["text"] = f"{amt} songs by {a}"

    elif s:
        artists = song_query(s)
        list_results.delete(0, tk.END)
        if len(artists) > 1:
            amt = 0
            for index, song in enumerate(sorted(artists, reverse=True)):
                list_results.insert(0, song)
                amt = index
        elif len(artists) == 1:
            pass
            #TODO: tell user there is only one artist
        else:
            pass
            #TODO: tell user there are no results

    else:
        #message that says you need to input something
        print("input something first...")


def handle_results_click(option: str) -> None:
    index = list_results.curselection()
    selection = option.widget.get(index)

    artist = artist_search_entry.get().strip()
    song = song_search_entry.get().strip()
    result = None

    if artist and not song:
        result = artist_and_song(artist, selection)

    elif song and not artist:
        result = artist_and_song(selection, song)
    
    #update the lyrics box
    lyrics_textbox.delete("1.0", tk.END)
    lyrics_textbox.insert("1.0", result)


def quit_gui() -> None:
    """Quit the program."""
#     cur.close()
#     con.close()
    quit()

def update_stats(records, artists):
    records_amt["text"] = record_count()
    artists_amt["text"] = artist_count()
