#std lib
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

#3rd party
import psycopg2

# custom
from db_util import *

# Database
# DB; "dbname=lyricsdemo user=postgres"
con = psycopg2.connect("dbname=lyricsdemo user=postgres")
cur = con.cursor()

root = tk.Tk()
root.geometry("1000x600")
root_color = "#%02x%02x%02x" % (235, 235, 235)
root.configure(bg=root_color)

s = ttk.Style()
s.configure(".", background="green")
s.configure("TButton", background="white")
s.configure("TEntry", background="white")


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
            search_results_frame["text"] = "{amt} artists"
        elif len(artists) == 1:
            search_results_frame["text"] = "Only one artist"
        else:
            search_results_frame["text"] = "No matches"

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
#         print("artist, no song:", artist_and_song(artist, selection))
        result = artist_and_song(artist, selection)

    elif song and not artist:
#         print("song, no artist:", artist_and_song(selection, song))
        result = artist_and_song(selection, song)
    
    #update the lyrics box
    lyrics_textbox.delete("1.0", tk.END)
    lyrics_textbox.insert("1.0", result)


def quit_gui() -> None:
    """Quit the program."""
    cur.close()
    con.close()
    quit()


################################################################################
# DB records
################################################################################
stats = ttk.LabelFrame(root, text="DB Stats")
# stats.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
stats.pack(tk.TOP)
stats.configure(bg=root_color, bd=2)

records_label = ttk.Label(stats, text="Records:")
records_label.grid(row=1, column=0, sticky=tk.W)
records_amt = ttk.Label(stats)
records_amt.grid(row=1, column=1, sticky=tk.E)

artists_label = ttk.Label(stats, text="Artists:")
artists_label.grid(row=2, column=0, sticky=tk.W)
artists_amt = ttk.Label(stats)
artists_amt.grid(row=2, column=1, sticky=tk.E)


################################################################################
# Files
################################################################################
# count_btn = ttk.Button(root, text="Count Files", command=lambda: count_files("Databases/data9"), style="TButton")
# count_btn.grid(row=0, column=1, sticky=tk.W, columnspan=4)

# file count = 38520
# progress_bar = ttk.Progressbar(root, length=100, mode="indeterminate", orient=tk.HORIZONTAL)
# progress_bar.grid(row=0, column=1)

file_amt = ttk.Label(root)
file_amt.grid(row=0, column=2, sticky=tk.E)


################################################################################
# Search Frame
################################################################################
search_frame = ttk.LabelFrame(root, text="Search")
search_frame.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10, columnspan=3)
# search_frame.configure(bg=root_color, bd=2)

artist_search_label = ttk.Label(search_frame, text="Artist:")
artist_search_label.grid(row=0, column=0, sticky=tk.W)

artist_search_entry = ttk.Entry(search_frame, style="TEntry", width=40)
artist_search_entry.grid(row=0, column=1, sticky=tk.E, columnspan=2)

song_search_label = ttk.Label(search_frame, text="Song:")
song_search_label.grid(row=1, column=0, sticky=tk.W)

song_search_entry = ttk.Entry(search_frame, style="TEntry", width=40)
song_search_entry.grid(row=1, column=1, sticky=tk.E, columnspan=2)

word_phrase_label = ttk.Label(search_frame, text="Exact word or phrase:")
word_phrase_label.grid(row=2, column=0, sticky=tk.W)

word_phrase_entry = ttk.Entry(search_frame, width=40)
word_phrase_entry.grid(row=2, column=1, sticky=tk.E)

search_btn = ttk.Button(search_frame, text="Search Lyrics", command=search)
search_btn.grid(row=3, column=0, sticky=tk.W)


################################################################################
# Search Results
################################################################################
search_results_frame = tk.LabelFrame(search_frame, text="Results")
search_results_frame.grid(row=9, column=0, sticky=tk.W, columnspan=2, padx=10, pady=10)
search_results_frame.configure(bd=2, bg=root_color)

search_results = ["Search for something"]
list_items = tk.StringVar(value=search_results)


list_results = tk.Listbox(search_results_frame, width=40, height=15, listvariable=list_items, selectmode=tk.SINGLE)
# list_results = tk.scrolledtext.ScrolledText(search_results_frame, height=15)
list_results.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
list_results.bind("<<ListboxSelect>>", handle_results_click)
# scrollbar = tk.Scrollbar(list_results)
# scrollbar.config(command=list_results.yview)
# list_results.config(yscrollcommand=scrollbar.set)

lyrics_textbox = tk.scrolledtext.ScrolledText(search_results_frame, height=20, width=60, wrap=tk.WORD)
lyrics_textbox.grid(row=0, column=1, sticky=tk.E, padx=10, pady=10)



# Quit button
quit_btn = ttk.Button(root, text="Quit", command=quit_gui)
quit_btn.grid(row=4, column=1, sticky=tk.E, columnspan=3)


if __name__ == "__main__":
    #preload some simple stats
    records_amt["text"] = record_count()
    artists_amt["text"] = artist_count()

    # main
    root.mainloop()
