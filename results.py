#std lib
import csv
import tkinter as tk
import re
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from typing import Text, List

#custom
import db_util

class Results(tk.Frame):
    list_ = None
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
        self.list_.bind("<<ListboxSelect>>", self.handle_results_click)
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


    @classmethod
    def delete_list(cls) -> None:
        if cls.list_:
            cls.list_.delete("1.0", tk.END)

    @classmethod
    def delete_lyrics(cls) -> None:
        if cls.lyrics:
            cls.lyrics.delete("1.0", tk.END)


    def _clear_results_list(self) -> None:
        self.list_.delete(0, tk.END)


    def _clear_results_list(self) -> None:
        self.list_.delete(0, tk.END)


    def _clear_lyrics(self) -> None:
        self.lyrics.delete("1.0", tk.END)


    def _save_search_results(self, string: Text, data: List) -> None:
        if self.ask_to_save(string):
            save_file = filedialog.asksaveasfilename()
            if save_file:
                with open(save_file, "w+") as f:
                    writer = csv.writer(f, delimiter="|")
                    writer.writerows(data)


    def _update_lyrics_box(self, data: List) -> None:
        self.lyrics.insert("1.0", data)


    def _update_results_list(self, data: List) -> None:
        self.list_.insert(0, data)


    def ask_to_save(self, string: str) -> bool:
        return messagebox.askyesno(title="Save to File?", message=f"Search for '{string}' is complete. Would you like to save the results to a CSV file? You can reload the results into other programs like Excel.")


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


    def long_search_message(self) -> bool:
        """Displays 'yes/no' confirmation to user if the search may take a long time."""
        return messagebox.askyesno(title="Word or Phrase Search", message="This may take up to 30 minutes. You may continue to use the program to search while waiting. The word entry field and word gap option will be disabled until the search is completed. A notification will appear when the search is finished. Are you sure you want to continue?")


    def reset(self) -> None:
        self._clear_results_list()


    def reset_list(self) -> None:
        self._clear_results_list()


    def reset_lyrics(self) -> None:
        self._clear_lyrics()


    def save_results(self, string: Text, data: List) -> None:
        self._save_search_results(self, string, data)


    def show_lyrics(self, data) -> None:
        """Load the lyrics results into the text box."""
        self.reset_lyrics()
        if data:
            self._update_lyrics_box(data)
        else:
            self._update_lyrics_box(["No matching results."])


    def show_songs(self, data: List) -> None:
        """Load the song and artist results into the list box."""
        self.clear_lyrics()
        self.clear_list()
        if len(data) > 1:
            for index, record in enumerate(sorted(data, reverse=True)):
                song, artist = record[1].title(), record[0].title()
#                 self.show_results(f'"{song}" by {artist}')
                self.show_results(data)
        elif len(data) == 1:
            song, artist = data[0][1].title(), data[0][0].title()
#             self.show_results(f'"{song}" by {artist}')
            self.show_results(data)
            lyrics = artist_and_song("songs", artist, song)
            self.show_lyrics(lyrics)
        else:
            self.show_results(["No matching results."])


    def show_results(self, data: List[Text]) -> None:
        if len(data) > 100:
            view_now = messagebox.askyesno(title="Show Results?", message=f"There are {len(data)} results. Viewing all of them at once may slow down your computer. Do you want to view all of them now?")
            if view_now:
                #TODO: make this threaded
                name_pairs = [pathlib.Path(record.file).stem.split("_") for record in self.regex_results]
                artist_songs = [(pair[0], pair[1]) for pair in name_pairs]
                self.show_songs(artist_songs)



