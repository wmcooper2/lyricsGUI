#std lib
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



class LyricsTab(tk.Frame):

    def __init__(self, master):
        super().__init__()

        self.search = Search(self)
        self.results = Results(self)

        #TODO: make regex results a class attribute in Results
        # it should be accessible everywhere for reading and have the same data everywhere
#         self.step = 100
#         self.regex = None

        # Quit button
        self.quit_btn = ttk.Button(self, text="Quit", command=self.quit_gui)
        self.quit_btn.grid(row=3, column=0, columnspan=10, sticky=tk.E+tk.W)
        self.quit_btn.grid_columnconfigure(0, weight=1)  # allows expansion of columns and rows?

    def cancel_search(self) -> None:
        self.search.cancel_search()
    
    def clear_lyrics(self) -> None:
        self.results.clear_lyrics()

    def clear_results(self) -> None:
        self.results.clear_results()
        self.results.clear_results_list()

    def reset_search(self) -> None:
        self.search.reset()

    def save_results(self, string: Text, data: List) -> None:
        self.results.save_results(string, data)

    def show_lyrics(self, data) -> None:
        self.results.show_lyrics(data)
    
    def show_results(self, data) -> None:
        Results.search_results = data
        self.results.show_results(data)

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
        #shut down any running threads
        self.cancel_search()
        # threads.join() ?
        quit()
