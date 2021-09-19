#std lib
import tkinter as tk
from tkinter import ttk

#3rd party
import psycopg2

# custom
from db_util import *

con = psycopg2.connect("dbname=lyricsdemo user=postgres")
cur = con.cursor()


root_color = "#%02x%02x%02x" % (235, 235, 235)

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





class App():
    def __init__(self, master):
        self.master = master
        master.title("A simple GUI")

        self.stats = Stats(master)
        self.stats.pack()

        self.search = Search(master)
        self.search.pack()

        self.quit_button = Footer(master)
        self.quit_button.pack()

    def greet(self):
        print("Greetings!")


class Row():
    def __init__(self, master, label):
        self.master = master
        self.label = ttk.Label(master, text=label)
        self.entry = ttk.Entry(master, style="TEntry", width=40)

    def pack(self):
        self.label.pack(side=tk.LEFT)
        self.entry.pack(side=tk.LEFT)

class Search():
    def __init__(self, master):
        self.master = master
        self.search_frame = tk.LabelFrame(master, text="Search", borderwidth=0)
        self.search_frame.configure(bg=root_color, bd=2)

        self.artist = Row(master, "Artist:", ) 
        self.artist.pack()

        self.song = Row(master, "Song:")
        self.song.pack()

        self.phrase = Row(master, "Word or Phrase:") 
        self.phrase.pack()
            
        self.search_btn = ttk.Button(master, text="Search Lyrics", command=search)
        self.search_btn.pack(side=tk.RIGHT)

    def pack(self):
        self.search_frame.pack(side=tk.TOP)



class Stats():
    def __init__(self, master):
        self.master = master
        self.stats = tk.LabelFrame(master, text="DB Stats")

        self.records_label = ttk.Label(master, text="Records:")
        self.records_label.pack(side=tk.LEFT, expand=True)

        self.records_amt = ttk.Label(master)
        self.records_amt.pack(side=tk.LEFT, expand=True)

        self.artists_label = ttk.Label(master, text="Artists:")
        self.artists_label.pack(side=tk.LEFT)

        self.artists_amt = ttk.Label(master)
        self.artists_amt.pack(side=tk.LEFT)

    def pack(self):
        self.stats.pack(side=tk.TOP)


class Footer():
    def __init__(self, master):
        self.master = master
        self.quit_btn = ttk.Button(master, text="Quit")

    def pack(self):
        self.quit_btn.pack()



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
