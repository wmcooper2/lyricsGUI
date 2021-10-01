#std lib
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

class Results(tk.Frame):
    search_results = None
    list_items = None
    lyrics = None

    def __init__(self, master):
        super().__init__()
#         self.root = ttk.LabelFrame(master, text="Results")
        self.root = ttk.LabelFrame(master)
        self.root.grid(row=2, column=0, sticky=tk.E+tk.W)
        self.root.grid_columnconfigure(0, weight=1)  # allows expansion of columns and rows?

        # TODO:text results frame
        self.search_results = [""]
        self.list_items = tk.StringVar(value=self.search_results)
        Results.search_results = self.search_results
        Results.list_items = self.list_items

        # song/artist results
        self.artist_song_results_frame = ttk.LabelFrame(self.root, text="Songs by Artist")
        self.artist_song_results_frame.grid(row=0, column=0, sticky=tk.E+tk.W+tk.N+tk.S)
        self.list_ = tk.Listbox(self.artist_song_results_frame, width=45, height=20, listvariable=self.list_items, selectmode=tk.SINGLE)
        self.list_.bind("<<ListboxSelect>>", master.handle_results_click)
        self.list_.grid(row=0, column=0, sticky=tk.E+tk.W+tk.N+tk.S, padx=5, pady=5)
        self.scrollbar = tk.Scrollbar(self.list_)
        self.scrollbar.config(command=self.list_.yview)
        self.list_.config(yscrollcommand=self.scrollbar.set)

        # lyrics results
        self.lyrics_results_frame = ttk.LabelFrame(self.root, text="Lyrics")
        self.lyrics_results_frame.grid(row=0, column=1, sticky=tk.E+tk.W+tk.N+tk.S)
        self.lyrics = tk.scrolledtext.ScrolledText(self.lyrics_results_frame, height=25, width=60, wrap=tk.WORD)
        Results.lyrics = self.lyrics
        self.lyrics.grid(row=0, column=0, sticky=tk.E+tk.W+tk.N+tk.S, padx=5, pady=5)
        self.lyrics.tag_configure("highlight", background="yellow", foreground="black")


