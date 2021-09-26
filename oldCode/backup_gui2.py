#std lib
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

#3rd party
import psycopg2

# custom
from db_util import *

con = psycopg2.connect("dbname=lyricsdemo user=postgres")
cur = con.cursor()

root_color = "#%02x%02x%02x" % (235, 235, 235)
# root.configure(bg=root_color)

s = ttk.Style()
s.configure(".", background="green")
s.configure("TButton", background="white")
s.configure("TEntry", background="white")


# delete?
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
        result = artist_and_song(selection, song)
    
    #update the lyrics box
    lyrics_textbox.delete("1.0", tk.END)
    lyrics_textbox.insert("1.0", result)


def quit_gui() -> None:
    """Quit the program."""
    cur.close()
    con.close()
    quit()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.stats = Stats(self)
        self.search = Search(self)
        self.results = Results(self)
        self.footer = Footer(self)

        self.stats.pack(side=tk.TOP, fill=tk.BOTH)
        self.search.pack(side=tk.TOP, fill=tk.X)
        self.results.pack(side=tk.TOP)

        self.footer.pack(side=tk.TOP)


class Stats(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.stats = tk.LabelFrame(self, text="DB Stats")
#         self.stats.configure(bg=root_color, bd=2)

        self.records_label = ttk.Label(self, text="Records:")
        self.records_label.pack(side=tk.LEFT, expand=True)

        self.records_amt = ttk.Label(self)
        self.records_amt.pack(side=tk.LEFT, expand=True)

        self.artists_label = ttk.Label(self, text="Artists:")
        self.artists_label.pack(side=tk.LEFT)

        self.artists_amt = ttk.Label(self)
        self.artists_amt.pack(side=tk.LEFT)


################################################################################
# Files
################################################################################
# count_btn = ttk.Button(root, text="Count Files", command=lambda: count_files("Databases/data9"), style="TButton")
# count_btn.grid(row=0, column=1, sticky=tk.W, columnspan=4)

# file count = 38520
# progress_bar = ttk.Progressbar(root, length=100, mode="indeterminate", orient=tk.HORIZONTAL)
# progress_bar.grid(row=0, column=1)

# file_amt = ttk.Label(root)
# file_amt.grid(row=0, column=2, sticky=tk.E)


class Row(ttk.LabelFrame):
    def __init__(self, parent, label):
        super().__init__(parent)
        self.label = ttk.Label(self, text=label)
        self.entry = ttk.Entry(self, style="TEntry", width=40)
        self.label.pack(side=tk.LEFT)
        self.entry.pack(side=tk.LEFT)


class Search(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.search_frame = tk.LabelFrame(self, text="Search", borderwidth=0)
        self.search_frame.configure(bg=root_color, bd=2)

        self.artist = Row(self, "Artist:", ) 
        self.artist.pack(side=tk.TOP, fill=tk.X)

        self.song = Row(self, "Song:")
        self.song.pack(side=tk.TOP, fill=tk.X)

        self.phrase = Row(self, "Word or Phrase:") 
        self.phrase.pack(side=tk.TOP, fill=tk.X)
            
        self.search_btn = ttk.Button(self, text="Search Lyrics", command=search)
        self.search_btn.pack(side=tk.RIGHT)


################################################################################
# Search Results
################################################################################
class Results(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.search_results_frame = tk.LabelFrame(self, text="Results")
        self.search_results_frame.configure(bd=2, bg=root_color)

        self.search_results = ["Search for something"]
        self.list_items = tk.StringVar(value=self.search_results)

        self.list_results = tk.Listbox(self, width=40, height=15, listvariable=self.list_items, selectmode=tk.SINGLE)
        self.list_results.pack(side=tk.LEFT)
        self.list_results.bind("<<ListboxSelect>>", handle_results_click)

        self.lyrics_textbox = tk.scrolledtext.ScrolledText(self, height=20, width=60, wrap=tk.WORD)
        self.lyrics_textbox.pack(side=tk.LEFT)


class Footer(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.quit_btn = ttk.Button(self, text="Quit", command=quit_gui)


if __name__ == "__main__":
    #preload some simple stats
#     window = tk.Tk()
#     root = tk.Tk()
#     app = App(root)
    app = App()
    app.mainloop()
#     app.stats.records_amt["text"] = record_count()
#     app.stats.artists_amt["text"] = artist_count()

    # main
#     root.mainloop()
