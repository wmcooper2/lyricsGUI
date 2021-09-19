#std lib
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

#3rd party
import psycopg2

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
    cur.close()
    con.close()
    quit()


if __name__ == "__main__":

    frame_padding = {"padx": 10, "pady": 10}

    #TODO: switch to sqlite3
    # main
        # Database
    # DB; "dbname=lyricsdemo user=postgres"
    con = psycopg2.connect("dbname=lyricsdemo user=postgres")
    cur = con.cursor()

    root = tk.Tk()
    root.geometry("1000x600")
    root_color = "#%02x%02x%02x" % (235, 235, 235)
    root.configure(bg=root_color)

    # s = ttk.Style()
    # s.configure(".", background="green")
    # s.configure("TButton", background="white")
    # s.configure("TEntry", background="white")

    ################################################################################
    # DB records
    ################################################################################
    stats = ttk.Frame(root)
#     stats.configure(bg=root_color, bd=2)
    stats.pack(side=tk.TOP, fill=tk.X, **frame_padding)

    records_label = ttk.Label(stats, text="Records:")
    records_label.pack(side=tk.LEFT)
    records_amt = ttk.Label(stats)
    records_amt.pack(side=tk.LEFT)

    artists_label = ttk.Label(stats, text="Artists:")
    artists_label.pack(side=tk.LEFT)
    artists_amt = ttk.Label(stats)
    artists_amt.pack(side=tk.LEFT)


    ################################################################################
    # Files
    ################################################################################
    # count_btn = ttk.Button(root, text="Count Files", command=lambda: count_files("Databases/data9"), style="TButton")
    # count_btn.pack()

    # file count = 38520
    # progress_bar = ttk.Progressbar(root, length=100, mode="indeterminate", orient=tk.HORIZONTAL)
    # progress_bar.pack()

#     file_amt = ttk.Label(root)
#     file_amt.pack()


    ################################################################################
    # Search Frame
    ################################################################################
    search_frame = ttk.LabelFrame(root, text="Search")
    search_frame.pack(side=tk.TOP, fill=tk.X, **frame_padding)
    # search_frame.configure(bg=root_color, bd=2)

    # row container
    artist_search = ttk.Frame(search_frame)
    artist_search.pack(side=tk.TOP, fill=tk.X)
    artist_search_label = ttk.Label(artist_search, text="Artist:")
    artist_search_label.pack(side=tk.LEFT)
    artist_search_entry = ttk.Entry(artist_search, style="TEntry", width=40)
    artist_search_entry.pack(side=tk.LEFT)

    # row container
    song_search = ttk.Frame(search_frame)
    song_search.pack(side=tk.TOP, fill=tk.X)
    song_search_label = ttk.Label(song_search, text="Song:")
    song_search_label.pack(side=tk.LEFT)
    song_search_entry = ttk.Entry(song_search, style="TEntry", width=40)
    song_search_entry.pack(side=tk.LEFT)

    word_search = ttk.Frame(search_frame)
    word_search.pack(side=tk.TOP, fill=tk.X)
    word_phrase_label = ttk.Label(word_search, text="Word or phrase:")
    word_phrase_label.pack(side=tk.LEFT)
    word_phrase_entry = ttk.Entry(word_search, width=40)
    word_phrase_entry.pack(side=tk.LEFT)

    search_btn = ttk.Button(search_frame, text="Search Lyrics", command=search)
    search_btn.pack(side=tk.RIGHT)


    ################################################################################
    # Search Results
    ################################################################################
    search_results_frame = tk.Frame(root)
    search_results_frame.pack(fill=tk.BOTH, **frame_padding)
    search_results_frame.configure(bd=2, bg=root_color)
    search_results = ["Search for something"]
    list_items = tk.StringVar(value=search_results)

    list_results = tk.Listbox(search_results_frame, width=40, height=15, listvariable=list_items, selectmode=tk.SINGLE)
#     list_results = tk.scrolledtext.ScrolledText(search_results_frame, height=15)
    list_results.bind("<<ListboxSelect>>", handle_results_click)
    list_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(list_results)
    scrollbar.config(command=list_results.yview)
    list_results.config(yscrollcommand=scrollbar.set)

    lyrics_textbox = tk.scrolledtext.ScrolledText(search_results_frame, height=20, width=60, wrap=tk.WORD)
    lyrics_textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)



    # Quit button
    quit_btn = ttk.Button(root, text="Quit", command=quit_gui)
    quit_btn.pack(side=tk.RIGHT)



    #preload some simple stats
    records_amt["text"] = record_count()
    artists_amt["text"] = artist_count()



    root.mainloop()
