#std lib
from collections import namedtuple
import csv
import logging
import pathlib
from pprint import pprint
import re
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from typing import Text, List

#custom
import db_util

DisplayRecord = namedtuple("DisplayRecord", ["artist", "song"])
logging.basicConfig(filename='Logs/errors.log', encoding='utf-8', level=logging.DEBUG)

class Results(tk.Frame):
    lyrics = None
    search_results = []

    def __init__(self, master):
        super().__init__()
#         self.root = ttk.LabelFrame(master, text="Results")
        self.root = ttk.LabelFrame(master)
        self.root.grid(row=2, column=0, sticky=tk.E+tk.W)
        self.root.grid_columnconfigure(0, weight=1)  # allows expansion of columns and rows?

        # song/artist results
        self.list_items = tk.StringVar(value=Results.search_results)
        self.artist_song_results_frame = ttk.LabelFrame(self.root, text="Songs by Artist")
        self.artist_song_results_frame.grid(row=0, column=0, sticky=tk.E+tk.W+tk.N+tk.S)
        self.list_ = tk.Listbox(self.artist_song_results_frame, width=45, height=20, listvariable=self.list_items, selectmode=tk.SINGLE)
        self.list_.bind("<<ListboxSelect>>", self.handle_results_click)
        self.list_.grid(row=0, column=0, sticky=tk.E+tk.W+tk.N+tk.S, padx=5, pady=5)
        self.scrollbar = tk.Scrollbar(self.list_)
        self.scrollbar.config(command=self.list_.yview)
        self.list_.config(yscrollcommand=self.scrollbar.set)

        # lyrics results
        self.lyrics_results_frame = ttk.LabelFrame(self.root, text="Lyrics")
        self.lyrics_results_frame.grid(row=0, column=1, sticky=tk.E+tk.W+tk.N+tk.S)
        self.lyrics = tk.scrolledtext.ScrolledText(self.lyrics_results_frame, height=25, width=60, wrap=tk.WORD)
#         Results.lyrics = self.lyrics
        self.lyrics.grid(row=0, column=0, sticky=tk.E+tk.W+tk.N+tk.S, padx=5, pady=5)
        self.lyrics.tag_configure("highlight", background="yellow", foreground="black")


    @classmethod
    def clear_results(cls) -> None:
        if cls.search_results:
            cls.search_results = []

    @classmethod
    def clear_lyrics(cls) -> None:
        if cls.lyrics:
            cls.lyrics.delete("1.0", tk.END)


    def ask_to_save(self, string: str) -> bool:
        #if string is None...
        return messagebox.askyesno(title="Save to File?", message=f"Search for '{string}' is complete. Would you like to save the results to a CSV file? You can reload the results into other programs like Excel.")


    def clear_results_list(self) -> None:
        self.list_.delete(0, tk.END)


#     def _insert_into_results_list(self, song: Text, artist: Text) -> None:
#         self.list_.insert(0, f"'{song}' by {artist}")


    def handle_results_click(self, option: str) -> None:
        """Load the selected song's lyrics into the lyrics box."""
        selection = None
        index = self.list_.curselection()
        try:
            selection = option.widget.get(index)
        except tk.TclError:
            logging.debug(f"TypeError: handle_results_click(), {selection}")
        song_match = None
        if selection:
            try:
                song_match = re.match('\".*?\"', selection)
            except TypeError:
                logging.debug(f"TypeError: handle_results_click(), couldn't extract song_name from quotes, {selection}")
                song_match = None
        song = None
        artist = None
        if song_match:
            song = song_match.group(0)
            song = selection[1:song_match.end()-1]
            # drop string through quotes
            by = " by "
            artist = selection[song_match.end()+len(by):]
            lyrics = db_util.artist_and_song("songs", artist, song)
            self.show_lyrics(lyrics)


    def highlight_lyrics(self, lyrics: Text, words: List) -> None:
        """Highlight the 'words'."""
        pass
        #TODO: no highlighting is happening...
        if lyrics:
            box = self.lyrics
            for tag in box.tag_names():
                box.tag_delete(tag)
            patterns = [f"\\b{word}\\b" for word in words]
            for pattern in patterns:
                match = re.search(pattern, lyrics)
                start = f"1.{match.start()}"
                end = f"1.{match.end()}"
                box.tag_add("highlight", start, end)


    def reset(self) -> None:
        Results.clear_results()


    def save_results(self, data: List) -> None:
        save_file = filedialog.asksaveasfilename()
        if save_file:
            with open(save_file, "w+") as f:
                writer = csv.writer(f, delimiter="|")
                writer.writerows(data)


    def show_lyrics(self, data) -> None:
        """Load the lyrics results into the text box."""
        self.reset_lyrics()
        if data:
            self.update_lyrics_box(data)
        else:
            self.update_lyrics_box(["No matching results."])


    def show_results(self, records: List[DisplayRecord]) -> None:
        """Load the song and artist results into the list box."""

        self.clear_results_list()
        if len(records) == 1:
            if records[0].artist == "" and record[0].song == "":
                # show no match message
                self.list_.insert(0, "No matches found")
            else:
                lyrics = artist_and_song("songs", record.artist, record.song)
                self.show_lyrics(lyrics)

        elif len(records) > 100:
            view_now = messagebox.askyesno(title="Show Results?", message=f"There are {len(records)} results. Viewing all of them at once may slow down your computer. Do you want to view all of them now?")
            if view_now:
                #TODO: load results async
                for index, record in enumerate(sorted(records, reverse=True)):
                    song, artist = record.artist, record.song
                    self.list_.insert(0, f"'{record.song}' by {record.artist}")

            elif self.ask_to_save():
                self.save_results(records)

        else:
            # just show normally
            for index, record in enumerate(sorted(records, reverse=True)):
                self.list_.insert(0, f"'{record.song}' by {record.artist}")

    def update_lyrics_box(self, data: List) -> None:
        self.lyrics.insert("1.0", data)
