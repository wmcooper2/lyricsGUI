#std lib
from collections import namedtuple
import pathlib
from pprint import pprint
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import Any, List, Optional, Text

#custom
from results import Results
from search import Search


DisplayRecord = namedtuple("DisplayRecord", ["artist", "song"])


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

    def save_results(self, data: List) -> None:
        self.results.save_results(data)

    def show_lyrics(self, data) -> None:
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
