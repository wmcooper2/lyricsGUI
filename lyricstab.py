#std lib
from collections import namedtuple
import logging
import pathlib
from pprint import pprint
import re
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Any, List, Optional, Text

#custom
from results import Results
from search import Search


DisplayRecord = namedtuple("DisplayRecord", ["artist", "song"])
logging.basicConfig(filename='Logs/errors.log', encoding='utf-8', level=logging.DEBUG)


class LyricsTab(tk.Frame):

    def __init__(self, master):
        super().__init__()

        self.search = Search(self)
        self.results = Results(self)

        self.quit_btn = ttk.Button(self, text="Quit", command=self.quit_gui)
        self.quit_btn.grid(row=3, column=0, columnspan=10, sticky=tk.E+tk.W)
        self.quit_btn.grid_columnconfigure(0, weight=1)  # allows expansion of columns and rows?

    def ask_to_save(self, string: Text = None) -> bool:
        return self.results.ask_to_save(string)

    def cancel_search(self) -> None:
        self.search.cancel_search()
    
    def clear_lyrics(self) -> None:
        self.results.clear_lyrics()
        self.results.clear_lyrics_text()

    def clear_results(self) -> None:
        self.results.clear_results()
        self.results.clear_results_list()

    def handle_results_click(self, option: Text, list_: List[Text]) -> None:
        index = list_.curselection()

        try:
            selection = option.widget.get(index)
        except tk.TclError:
            logging.debug(f"TypeError: handle_results_click(), {selection}")
        song_match = None

        print("selection:", selection)
        if selection:
            try:
                song_match = re.match('\".*?\"', selection)
                #TODO: matching not working
                print("song_match:", song_match)
            except TypeError:
                logging.debug(f"TypeError: handle_results_click(), couldn't extract song_name from quotes, {selection}")
                song_match = None
        song = None
        artist = None

        if song_match:
            song = song_match.group(0)
            song = selection[1:song_match.end()-1]
            print("song", song)

            # drop string through quotes
            by = " by "
            artist = selection[song_match.end()+len(by):]
#             lyrics = db_util.artist_and_song("songs", artist, song)
            lyrics = self.search.db.artist_and_song("songs", artist, song)

            print("lyrics:", lyrics)
            self.show_lyrics(lyrics)

    def save_results(self, data: List) -> None:
        self.results.save_results(data)

    def show_lyrics(self, data: List) -> None:
        self.results.show_lyrics(data)
    
    def show_results(self, records: List[DisplayRecord], lyrics=None) -> None:
        Results.search_results = records
        self.results.show_results(records, lyrics=lyrics)

    def stop_search(self) -> None:
        self.search.stop()

    def tick_progress(self) -> None:
        self.search.tick_progress()

    def update_progress_label(self, string: Text) -> None:
        self.search.update_progress_label(string)

    def toggle_fuzzy_search(self) -> None:
        self.search.toggle_fuzzy_search()

    def quit_gui(self) -> None:
        """Quit the program."""
        self.cancel_search()
        # threads.join() ?
        quit()
