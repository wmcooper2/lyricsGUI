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
from typing import List, Text, Union

#custom
import database


DisplayRecord = namedtuple("DisplayRecord", ["artist", "song"])
DBRecord = namedtuple("DBRecord", ["id", "artist", "song", "lyrics"])
logging.basicConfig(filename='Logs/errors.log', encoding='utf-8', level=logging.DEBUG)


class Results(tk.Frame):
    lyrics = None
    search_results = []

    def __init__(self, master):
        super().__init__()
#         self.root = ttk.LabelFrame(master, text="Results")
        self.master = master
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
        """Clear all search results from the class attribute."""

        if cls.search_results:
            cls.search_results = []


    @classmethod
    def clear_lyrics(cls) -> None:
        """Clear the lyrics text from the class attribute."""

        if cls.lyrics:
            cls.lyrics.delete("1.0", tk.END)


    def ask_to_save(self, string: Text = None) -> bool:
        """Ask the user to save the data."""

        if string:
            message = f"Search for '{string}' is complete.\
                    Would you like to save the results to a CSV file?\
                    You can reload the results into other programs like Excel."
        else:
            message = "Search complete.\
                    Would you like to save the results to a CSV file?\
                    You can reload the results into other programs like Excel."
        return messagebox.askyesno(title="Save to File?", message=message)


    def clear_results_list(self) -> None:
        """Clear the list of search results."""

        self.list_.delete(0, tk.END)


    def clear_lyrics_text(self) -> None:
        """Clear the lyrics text."""

        self.lyrics.delete("1.0", tk.END)


    def handle_results_click(self, option: Text) -> None:
        """Load the selected song's lyrics into the lyrics box."""
        self.master.handle_results_click(option, self.list_)

#            song = song_match.group(0)
#            song = selection[1:song_match.end()-1]
#            # drop string through quotes
#            by = " by "
#            artist = selection[song_match.end()+len(by):]
#            lyrics = db_util.artist_and_song("songs", artist, song)
#            self.show_lyrics(lyrics)


    def highlight_lyrics(self, lyrics: Text, words: List) -> None:
        """Highlight the 'words' in the lyrics text."""

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


    def save_results(self, data: List) -> None:
        """Ask user for file name to save it as, then write to that file as a CSV."""

        save_file = filedialog.asksaveasfilename()
        if save_file:
            with open(save_file, "w+") as f:
                writer = csv.writer(f, delimiter="|")
                writer.writerows(data)


    def show_lyrics(self, lyrics: Text) -> None:
        """Load the lyrics results into the text box."""

        self.clear_lyrics_text()
        if lyrics:
            self.update_lyrics_box(lyrics)
        else:
            self.update_lyrics_box("No matching results.")


    def show_results(self, records: List[DisplayRecord]=None, lyrics=None) -> None:
        """Load the song and artist results into the list box."""

        self.clear_results_list()
        self.clear_lyrics_text()

        # wrap in list if a single record was given
        if isinstance(records, tuple):
            records = [records]

        if records is None:
            self.list_.insert(0, "No matches found")
        elif len(records) == 1:
            if records[0].artist == "" and records[0].song == "":
                self.list_.insert(0, "No matches found")
            elif lyrics:
                self.list_.insert(0, f"'{records[0].song}' by {records[0].artist}")
                self.show_lyrics(lyrics)

        elif len(records) > 500:
            view_now = messagebox.askyesno(title="Show Results?", message=f"There are {len(records)} results. Viewing all of them at once may slow down your computer. Do you want to view all of them now?")

            if view_now:
                #TODO: load results async
                for index, record in enumerate(sorted(records, reverse=True)):
                    song, artist = record.artist, record.song
#                     self.list_.insert(0, f"'{record.song}' by {record.artist}")
                    self.list_.insert(0, f"'{record.song}' by {record.artist}")

            elif self.ask_to_save():
                self.save_results(records)

        else:
            # just show normally
            for index, record in enumerate(sorted(records, reverse=True)):
                self.list_.insert(0, f"'{record.song}' by {record.artist}")

    def update_lyrics_box(self, data: Union[Text, database.DBRecord]) -> None:
        """Update the lyrics box with 'data'."""

        try: 
            data = data.lyrics
            
        except Exception as e:
            #TODO, log
            print(e)

        self.lyrics.insert("1.0", data)
