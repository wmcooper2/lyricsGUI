#std lib
import codecs
from collections import namedtuple
import concurrent.futures
import csv
import logging
import pathlib
from pprint import pprint
import re
import threading
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from typing import Any, Optional

#custom
from db_util import (
        artist2,
        artist_query,
        artist_and_song,
        fuzzy_artist,
        fuzzy_artist_and_song,
        fuzzy_song,
        index_search,
        song_query)
from results import Results
from search import Search


FileMatch = namedtuple("FileMatch", ["file", "match"])

def timing(function):
    """Timing decorator."""
    def wrapper(*args, **kwargs):
        start = time.time()
        function(*args, **kwargs)
        end = time.time()
        print("time taken:", function.__name__, end - start)
    return wrapper


class LyricsTab(tk.Frame):

    #TODO, make the list box accessible through @classmethod?

    def __init__(self, master):
        super().__init__()

        self.search = Search(self)
        self.results = Results(self)

        self.regex_results = []
        self.index = 0
        self.step = 100
        self.regex = None

        # conveniences
        self.search.artist.focus()

        # Quit button
        self.quit_btn = ttk.Button(self, text="Quit", command=self.quit_gui)
        self.quit_btn.grid(row=3, column=0, columnspan=10, sticky=tk.E+tk.W)
        self.quit_btn.grid_columnconfigure(0, weight=1)  # allows expansion of columns and rows?


    def _ask_to_display_results(self, amt: str) -> None:
        if amt > 100:
            view_now = messagebox.askyesno(title="Show Results?", message=f"There are {amt} results. Viewing all of them at once may slow down your computer. Do you want to view all of them now?")
            if view_now:
                #TODO: make this threaded
                name_pairs = [pathlib.Path(record.file).stem.split("_") for record in self.regex_results]
                artist_songs = [(pair[0], pair[1]) for pair in name_pairs]
                self.show_songs(artist_songs)


    def _clear_search_entry(self) -> None:
        self.search.words["text"] = " "


    def _clear_results_list(self) -> None:
        self.results.list_.delete(0, tk.END)


    def _clear_lyrics(self) -> None:
        self.results.lyrics.delete("1.0", tk.END)


    def _disable_word_entry(self) -> None:
        self.search.words.state(["disabled"])


    def _disable_word_gap_scale(self) -> None:
        self.search.slider.state(["disabled"])


    def _enable_word_entry(self) -> None:
        self.search.words.state(["!disabled"])


    def _enable_word_gap_scale(self) -> None:
        self.search.slider.state(["!disabled"])


    def _increment_progress(self) -> None:
        self.search.progress_bar.step(1)


    def _reset_cancel_flag(self) -> None:
        self.cancel_flag = False


    def _reset_index(self) -> None:
        self.index = 0


    def _save_search_results(self, string: str, data: list) -> None:
        if self.ask_to_save(string):
            save_file = filedialog.asksaveasfilename()
            if save_file:
                with open(save_file, "w+") as f:
                    writer = csv.writer(f, delimiter="|")
                    writer.writerows(data)


    def _stop_progress_bar(self) -> None:
        self.search.progress_bar.stop()


    def _update_progress_label(self, string: str) -> None:
        self.search.progress_label["text"] = string
        self.search.progress_bar["value"] = 0

    
    def _update_lyrics_box(self, data: list) -> None:
        self.results.lyrics.insert("1.0", data)

    
    def _update_results_list(self, data: list) -> None:
        self.results.list_.insert(0, data)


    def ask_to_cancel_search(self) -> bool:
        message = messagebox.askyesno(title="Cancel Current Search", message="Another search is currently in process. Do you wish to cancel that search and start a new one?")


    def ask_to_save(self, string: str) -> bool:
        return messagebox.askyesno(title="Save to File?", message=f"Search for '{string}' is complete. Would you like to save the results to a CSV file? You can reload the results into other programs like Excel.")


    def handle_results_click(self, option: str) -> None:
        """Load the selected song's lyrics into the lyrics box."""
        breakpoint()
        selection = None
        index = self.results.list_.curselection()
        try:
            selection = option.widget.get(index)
        except tk.TclError:
            logging.debug(f"TypeError: handle_results_click(), {selection}")
        song = None
        artist = None
        if selection:
            try:
                song_match = re.match('\".*?\"', selection)
            except TypeError:
                logging.debug(f"TypeError: handle_results_click(), couldn't extract song_name from quotes, {selection}")
                song_match = None

        if song_match:
            song = song_match.group(0)
            song = selection[1:song_match.end()-1]
            # drop string through quotes
            by = " by "
            artist = selection[song_match.end()+len(by):]
            lyrics = artist_and_song(artist, song)
            self.show_lyrics(lyrics)


    def highlight_lyrics(self, lyrics: str, words: list) -> None:
        """Highlight the 'words'."""
        pass
        #TODO: no highlighting is happening...
        if lyrics:
            box = self.results.lyrics
            for tag in box.tag_names():
                box.tag_delete(tag)
            patterns = [f"\\b{word}\\b" for word in words]
            for pattern in patterns:
                match = re.search(pattern, lyrics)
                start = f"1.{match.start()}"
                end = f"1.{match.end()}"
                box.tag_add("highlight", start, end)


    def regex_search(self, file_: pathlib.PosixPath) -> FileMatch:
        """Perform a regex search for 'pattern'."""
        with codecs.open(file_, "r", encoding="utf-8", errors="ignore") as f:
            match = None
            try:
                match = self.regex.search(f.read())
            except TypeError:
                logging.debug(f"TypeError: {file_}")
        #TODO: fix the increment
        self._increment_progress()
        return FileMatch(file_, match)


    #TODO: refactor
    def search(self) -> None:
        """Perform database query.

        Possible Search Patterns:
            Artist  X   X   X   O   X   O   O   O
            Song    X   X   O   X   O   X   O   O
            Word    X   O   X   X   O   O   X   O

        Personal note:
        Completed?
            Fuzzy   
            Exact  
        """

        # clear the listbox's contents
        self.results.list_.delete(0, tk.END)
        self.results.lyrics.delete("1.0", tk.END)

        # convienence vars
        a = self.search.artist.get().strip()
        s = self.search.song.get().strip()
        w = self.search.words.get().strip()

        fuzzy = self.search.fuzzy
        if fuzzy:
            #get value of the word gap scale
            word_gap = self.search.slider.get()

        artist_results = None
        song_results = None
        lyrics_results = None

        #TODO: finish fuzzy search option for word
        #TODO: Need to add highlighting to lyrics... having some trouble here

        #wsa: if that song by that artist exists, then highlight its lyrics
        if w and s and a:
            lyrics = None
            words = w.split(" ")
            if fuzzy:
                lyrics = fuzzy_artist_and_song(a, s)
            else:
                lyrics = artist_and_song(a, s)

            if lyrics:
                assert len(lyrics) == 1
                match = re.search(w, lyrics)
                #TODO: self.highlight_lyrics(lyrics, words)
            self.show_lyrics(lyrics)
            self.show_songs([(a, s)])

        #ws : load the song, then highlight its lyrics
        elif w and s and not a:
            if fuzzy:
                #find all songs that are similar
                artists = fuzzy_song(s)
                #TODO: ...then tag the lyrics

        #TODO: this one might be a little more involved...
        #w a: load all the songs by the artist, then for each song highlight the matching words
        elif w and not s and a:
            if fuzzy:
                #find all artists that are similar
                artists = fuzzy_song(s)

                #just load all the songs by the artist.
                #when a song is clicked, grab the lyrics from the DB and add tags on the spot

            else:
#                 artists = song_query(s)
                songs = song_query(a)
                #TODO; when song clicked, grab the lyrics from the DB and add tags on the spot
                self.show_songs(songs)

        # sa: show lyrics for that song from that artist
        elif not w and s and a:
            lyrics = None
            if fuzzy:
                lyrics = fuzzy_artist_and_song(a, s)
            else:
                lyrics = artist_and_song(a, s)

            if lyrics:
                self.show_songs([(a, s)])
            else:
                self.show_songs([])
                self.show_lyrics(lyrics)

        #w  : search for all the lyrics that contain that word
        elif w and not s and not a:
            if fuzzy:
                #TODO: implement a word gap fuzzy lookup
                # adapt self.word_search to call a thread with the gap argument
                # for lyrics in DB:
                    # search through each song for a match
                    # if match, put song and artist in results list
                gap = self.search.slider.get()
                self.fuzzy_word_search(w, self.search.song_count, gap)

            else:
                #TODO, rethink cancelling a threaded word search
#                 search_in_progress = self.search.button["text"] == "Cancel"
                search_in_progress = False
                if search_in_progress:
                    cancel = self.ask_to_cancel_search()
                    if cancel:
                        message = self.long_search_message()
                        if message:
                            self.word_search(w, self.search.song_count)
                else:
                    message = self.long_search_message()
                    if message:
                        self.word_search(w, self.search.song_count)

        # s : search for all artists who have written a song with the same name
        elif not w and s and not a:
            artists = None
            if fuzzy:
                artists = fuzzy_song(s)
            else:
                artists = artist_query(s)
            if artists:
                self.show_songs(artists)

        #  a: load all songs written by that artist
        elif not w and not s and a:
            if fuzzy:
                songs = fuzzy_artist(a)
            else:
                songs = artist2(a)
            self.show_songs(songs)

        #none, no input was given
        else:
            self.input_something_message()

    def fuzzy_thread_manager(self, pattern: str, limit: int, gap: int) -> None:
            """Main fuzzy-search thread."""
            #TODO: finish the threaded gap search
            start_time = time.time()
            while self.index < limit and not self.cancel_flag:

                #TODO: pass list of words...
                thread = threading.Thread(target=self.gap_search, args=(pattern, gap))

                thread.start()
                while thread.is_alive():        # wait for the thread to finish
                    continue
                thread.join()                   # end the thread, (timeout=5) ? 
                self.index += self.step
                if self.search.progress.get() >= self.search.song_count:
                    break
                self._increment_progress()
            end_time = time.time()
            time_taken = (end_time - start_time) / 60
            result_count = len(self.regex_results)

            # reset the gui after the threaded search is finished
            self._stop_progress_bar()
            self._reset_cancel_flag()
            self._update_progress_label(f"Search completed in {round(time_taken, 3)} minutes. {result_count} matches found.")
            self._reset_index()
            self._enable_word_entry()
            self._enable_word_gap_scale()
            self._save_search_results(pattern, self.regex_results)
            self._ask_to_display_results(result_count)


    def fuzzy_word_search(self, pattern: str, limit: int, gap: int):
        """Search for 'pattern' with max 'gap' between any pairs of neighboring words in 'pattern' through all lyrics."""
        #set up the gui for threaded search
        self._update_progress_label(f"Searching for: '{pattern}'...")
        self._clear_lyrics()
        self._clear_results_list()
        self._clear_search_entry()
        self._disable_word_entry()
        self._disable_word_gap_scale()
        self.regex_results = []
        self.cancel_flag = False
        self.index = 0
#         print(f"fuzzy_word_search(): pattern={pattern}, limit={limit}, gap={gap}")
#         print(f"{fuzzy_word_search.__name__}(), ")
        try:
            manager_thread = threading.Thread(target=self.fuzzy_thread_manager, args=(pattern, limit, gap))
            manager_thread.start()
        except RuntimeError:
            logging.debug(f"RuntimeError, {word_search.__name__}(): pattern={pattern}")


    def show_songs(self, data: list) -> None:
        """Load the song and artist results into the list box."""
        self._clear_lyrics()
        self._clear_results_list()

        if len(data) > 1:
            for index, record in enumerate(sorted(data, reverse=True)):
                song, artist = record[1].title(), record[0].title()
                self._update_results_list(f'"{song}" by {artist}')
        elif len(data) == 1:
            song, artist = data[0][1].title(), data[0][0].title()
            self._update_results_list(f'"{song}" by {artist}')
            lyrics = artist_and_song(artist, song)
            self.show_lyrics(lyrics)
        else:
            self._update_results_list(["No matching results."])


    def show_lyrics(self, data) -> None:
        """Load the lyrics results into the text box."""
        self._clear_lyrics()
        if data:
            self._update_lyrics_box(data)
        else:
            self._update_lyrics_box(["No matching results."])


#     def thread_manager(self, limit: int, regex: re.Pattern) -> None:
#     def thread_manager(self, limit: int, files: list, funct):
    @timing
    def thread_manager(self, limit: int, regex: re.Pattern):
        """Main search thread."""
        self.regex = regex
        results = set()

        #TODO, need files
        root_dir = "/Volumes/SILVER256"
        dirs = [f"{root_dir}/data{str(num)}" for num in range(1, 10)]
        files = list(pathlib.Path(dirs[0]).iterdir())

#         while self.index < limit and not self.cancel_flag:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.regex_search, file_) for file_ in files}
            for future in concurrent.futures.as_completed(futures):
                result = None
                try:
                    result = future.result()
                except TypeError as e:
                    logging.debug(f"TypeError: {file_}")
                if result.match:
                    results.add(result)
                    self.regex_results.append(result)

        result_count = len(self.regex_results)
        self._stop_progress_bar()
        self._reset_cancel_flag()
#         self._update_progress_label(f"Search completed in {round(time_taken, 3)} minutes. {result_count} matches found.")
        self._reset_index()
        self._enable_word_entry()
        self._enable_word_gap_scale()
        self._save_search_results(regex.pattern, self.regex_results)
        self._ask_to_display_results(result_count)


    def word_search(self, pattern: str, limit: int):
        """Search for 'pattern' in all lyrics."""
        #set up the gui for threaded search
        self._update_progress_label(f"Searching for: '{pattern}'...")
        self._clear_lyrics()
        self._clear_results_list()
        self._clear_search_entry()
        self._disable_word_entry()
        self._disable_word_gap_scale()

        regex = re.compile(pattern)
        self.regex_results = []
        self.cancel_flag = False
        try:
            # create main thread to manage the other threads
            manager_thread = threading.Thread(target=self.thread_manager, args=(limit, regex))
            manager_thread.start()
        except RuntimeError:
            logging.debug(f"RuntimeError, {word_search.__name__}(): pattern={pattern}")
            #TODO, figure out the use of "from None" in exception handling to return just the most recent exception traceback
#         except Exception as e from None


    def quit_gui(self) -> None:
        """Quit the program."""
        #shut down any running threads
        self.cancel_flag = True
        # threads.join() ?
        quit()


    def distant_neighboring_words(self, lyrics: list, words: list, gap: int) -> Any:
        """This algorithm is the heart of the gap_search() function."""

        if words:
            try:
                index = lyrics.index(words[0])
            except:
                index = None
            try:
                if index is not None:
                    if index > len(lyrics) - len(words) or index > gap:
                        return str(False)
                    return str(index) + str(self.distant_neighboring_words(lyrics[index+1:], words[1:], gap))
                else:
                    return str(False)
            except ValueError:  # word not found in lyrics 
                logging.debug(f"ValueError: {words}")
                return str(False)
        else:
            return str(True)

 
#     def gap_search(self, lyrics: list=None, words: list=None, gap: int=0) -> list:
    def gap_search(self, words: str="", gap: int=0) -> list:
        """Searches for all 'words' with max 'gap' between any neighboring pair of words."""

        def _gap_search_result(result: str) -> bool:
            """Convert the result into a boolean."""
            #TODO: 
            if result.endswith("True"):
                final_seq = result.rstrip("True")
                return True
            else:
                return False

        #start here
        if words:
            gap = int(gap)
            for i, artist, song, lyrics in index_search(self.index, self.step):
                if lyrics is not None and words is not None:
                    lyrics = lyrics.split(" ")
                    words = words.split(" ")
                    #TODO: remove punct from words and lyrics? 
                    answer = self.distant_neighboring_words(lyrics, words, gap)
                    return _gap_search_result(answer)
        return []


    def long_search_message(self) -> bool:
        """Displays 'yes/no' confirmation to user if the search may take a long time."""
        return messagebox.askyesno(title="Word or Phrase Search", message="This may take up to 30 minutes. You may continue to use the program to search while waiting. The word entry field and word gap option will be disabled until the search is completed. A notification will appear when the search is finished. Are you sure you want to continue?")


    def input_something_message(self) -> None:
        """Advises user to input something if they haven't."""
        messagebox.showinfo(title="Advice", message="Input something to begin a search.")
