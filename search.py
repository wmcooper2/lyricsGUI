#std lib
import codecs
from collections import namedtuple
import concurrent.futures
import logging
import pathlib
import re
import threading
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from typing import Any, List, Optional, Text, Tuple

#custom
import db_util
from results import Results



FileMatch = namedtuple("FileMatch", ["file", "match"])
Query = namedtuple("Query", ["artist", "song", "grammar"])
DisplayRecord = namedtuple("DisplayRecord", ["artist", "song"])
logging.basicConfig(filename='Logs/errors.log', encoding='utf-8', level=logging.DEBUG)

def timing(function):
    """Timing decorator."""
    def wrapper(*args, **kwargs):
        start = time.time()
        function(*args, **kwargs)
        end = time.time()
        print("time taken:", function.__name__, end - start)
    return wrapper


class Search(tk.Frame):
    def __init__(self, master):
        super().__init__()

        self.results = []
        self.master = master
        self.fuzzy = False
        self.cancel_flag = False
        self.search_in_progress = False
        self.index = 0
        self.song_count = db_util.record_count("Databases/lyrics.db", "songs")
        self.artist_count = db_util.artists("songs")

#         self.root = ttk.LabelFrame(master, text="Search")
        self.root = ttk.Frame(master)
        self.root.grid(row=1, column=0)

        # ENTRY FRAME
        self.entry_frame = ttk.Frame(self.root)
        self.entry_frame.grid(row=0, column=0, sticky=tk.W)

        # OPTIONS FRAME
        self.options_frame = ttk.Frame(self.root)
        self.options_frame.grid(row=0, column=1, sticky=tk.E)

        # search entry rows
        self.artist_frame = ttk.Frame(self.entry_frame)
        self.artist_frame.grid(row=0, column=0)
        self.artist_search_label = ttk.Label(self.artist_frame, text="Artist:", width=15)
        self.artist_search_label.grid(row=0, column=0)
        self.artist = ttk.Entry(self.artist_frame, style="TEntry", width=40)
        self.artist.grid(row=0, column=1)

        # song row
        self.song_frame = ttk.Frame(self.entry_frame)
        self.song_frame.grid(row=1, column=0)
        self.song_search_label = ttk.Label(self.song_frame, text="Song:", width=15)
        self.song_search_label.grid(row=0, column=0)
        self.song = ttk.Entry(self.song_frame, style="TEntry", width=40)
        self.song.grid(row=0, column=1)

        # word row
        self.word_frame = ttk.Frame(self.entry_frame)
        self.word_frame.grid(row=2, column=0)
        self.word_phrase_label = ttk.Label(self.word_frame, text="Word or phrase:", width=15)
        self.word_phrase_label.grid(row=0, column=0)
        self.words = ttk.Entry(self.word_frame, width=40)
        self.words.grid(row=0, column=1)

        # exact/fuzzy options
        self.radiobutton_frame = ttk.Frame(self.options_frame)
        self.radiobutton_frame.grid(row=0, column=0, sticky=tk.E)
        self.artist_option_var = tk.StringVar()

        # exact option
        self.artist_option_exact = ttk.Radiobutton(self.radiobutton_frame, text="Exact", variable=self.artist_option_var, value=1, command=self.disable_fuzzy_search)
        self.artist_option_exact.grid(row=0, column=0)
        self.artist_option_exact.state(["selected"])

        # fuzzy option
        self.artist_option_fuzzy = ttk.Radiobutton(self.radiobutton_frame, text="Fuzzy", variable=self.artist_option_var, value=2, command=self.enable_fuzzy_search)
        self.artist_option_fuzzy.grid(row=0, column=1)

        # max words between
        self.slider_var = tk.IntVar()
        self.slider_frame = ttk.Frame(self.options_frame)
        self.slider_frame.grid(row=1, column=0, sticky=tk.E)
        self.slider_label = ttk.Label(self.slider_frame, text=f"Word gap: {self.slider_var.get()}")
        self.slider_label.grid(row=0, column=0)
        self.slider = ttk.Scale(self.slider_frame, from_=0, to=5, command=self.update_scale, variable=self.slider_var)
        self.slider.grid(row=0, column=1)
        self.slider.state(["disabled"])

        # search/cancel button
        #TODO, change to "Cancel" when search in progress
        self.button = ttk.Button(self.root, text="Search", command=self.search)
        self.button.grid(row=2, column=10, columnspan=10)

        #TODO, change the maximum of the progress_bar
        self.progress = tk.IntVar()
        self.progress_label = ttk.Label(self.root, text="Searching for: Nothing yet...")
        self.progress_label.configure(font="Helvetica 12 italic")
        self.progress_label.grid(row=1, column=0, sticky=tk.W, padx=10)
        self.progress_bar = ttk.Progressbar(self.root, length=800, maximum=self.song_count, mode="determinate", variable=self.progress)
        self.progress_bar.grid(row=2, column=0, columnspan=9)
        self.artist.focus()


    def clear_search(self) -> None:
        self.words["text"] = " "
        self.song["text"] = " "
        self.artist["text"] = " "


    def cancel_search(self) -> bool:
        if self.search_in_progress:
            message = "Another search is currently in process.\
                    Do you wish to cancel that search and start a new one?"
            if messagebox.askyesno(title="Cancel Current Search", message=message):
                self.stop()

#         return message


    def clear_results(self) -> None:
        self.master.clear_results()


    def clear_lyrics(self) -> None:
        self.master.clear_lyrics()


    def disable_fuzzy_search(self):
        self.fuzzy = False
        self.slider.state(["disabled"])


    def distant_neighboring_words(self, lyrics: List, words: List, gap: int) -> Any:
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


    def enable_fuzzy_search(self):
        self.fuzzy = True
        self.slider.state(["!disabled"])


    def exact_search(self, query: Query):
        #match artist and song, then search for grammar
        self.master.clear_lyrics()
        self.master.clear_results()
        q = query

        #ARTIST     SONG    GRAMMAR
        #search for a song written by one artist, then search for grammar
        if q.artist and q.song and q.grammar:
            lyrics = None
            words = q.grammar.split(" ")
            lyrics = db_util.artist_and_song(q.artist, q.song)
            print("lyrics:", lyrics)
#             if lyrics:
#                 #refactor
#                 assert len(lyrics) == 1 # only 1, not more
#                 match = re.search(q.grammar, lyrics)
#             record = DisplayRecord(q.artist, q.song)
#             self.show_results([record])
#             self.show_lyrics(lyrics)

        #ARTIST     SONG
        #find artist and song
        elif q.artist and q.song and not q.grammar:
            lyrics = None
            lyrics = db_util.artist_and_song("songs", q.artist, q.song)
            print("lyrics:", lyrics)
#             if lyrics:
#                 record = DisplayRecord(q.artist, q.song)
#                 self.show_results([record])
#             else:
#                 record = DisplayRecord("", "")
#                 self.show_results(record)
#                 self.show_lyrics(lyrics)

        #ARTIST             GRAMMAR
        #find grammar within all songs written by one artist
        elif q.artist and not q.song and q.grammar:
#                 artists = db_util.song_query(q.song)
            songs = db_util.song_query(q.artist)
            print("songs:", songs)
            #convert to DisplayRecords
#             records = [DisplayRecord(song[0], song[1]) for song in songs]
#             self.show_results(records)

        #           SONG    GRAMMAR
        #match songs, then search for grammar within those songs
        elif not q.artist and q.song and q.grammar:
            #TODO, this block not finished, need to search through grammar
            songs = db_util.song_query(q.artist)
            print("songs:", songs)

        #                   GRAMMAR
        #search only for grammar in all songs
        elif not q.artist and not q.song and q.grammar:
            #TODO: rethink cancelling thread ability
            print("grammar search...:", q.grammar)
            search_in_progress = False
            if search_in_progress:
                message = self.long_search_message()
                if message:
                    self.word_search(q.grammar, self.song_count)
            else:
                message = self.long_search_message()
                if message:
                    self.word_search(q.grammar, self.song_count)

        #           SONG
        #search for all records with the same song name
        elif not q.artist and q.song and not q.grammar:
            records = db_util.artist_query("Databases/lyrics.db", "songs", q.song)
            if records:
                records = [DisplayRecord(record[0], record[1]) for record in records]
                self.show_results(records)

        #ARTIST
        #all songs by a single artist
        elif q.artist and not q.song and not q.grammar:
            songs = db_util.artist2("songs", q.artist)
            print("Entry - Artist:", songs[0])
            records = [DisplayRecord(song[0], song[1]) for song in songs]
            self.show_results(records)

        #NONE     NONE    NONE
        #ask user to input anything
        else:
            self.input_something_message()


    def fuzzy_search(self, query: Query):
        word_gap = self.slider.get()
        q = query
        if q.artist and q.song and q.grammar:
            lyrics = db_uitl.fuzzy_artist_and_song(q.artist, q.song)
        elif not q.artist and q.song and q.grammar:
            artists = db_util.fuzzy_song(q.song)
        elif q.artist and not q.song and q.grammar:
            #doesn't make sense
            artists = db_util.fuzzy_song(q.song)
        elif q.artist and q.song and not q.grammar:
            lyrics = db_uitl.fuzzy_artist_and_song(q.artist, q.song)
        elif not q.artist and not q.song and q.grammar:
            gap = self.slider.get()
            self.fuzzy_word_search(q.grammar, self.song_count, gap)
        elif not q.artist and q.song and not q.grammar:
            artists = db_util.fuzzy_song("Databases/lyrics.db", "songs", q.song)
        elif q.artist and not q.song and not q.grammar:
            songs = db_util.fuzzy_artist("Databases/lyrics.db", "songs", q.artist)
        else:
            self.input_something_message()


    def fuzzy_manager(self, pattern: str, limit: int, gap: int) -> None:
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
                if self.progress.get() >= self.song_count:
                    break
                self.tick_progress()
            end_time = time.time()
            time_taken = (end_time - start_time) / 60
            result_count = len(self.results)
            # reset the gui after the threaded search is finished
#             self._stop_progress_bar()
            self.stop()
            self.update_progress_label(f"Search completed in {round(time_taken, 3)} minutes. {result_count} matches found.")
            self.toggle_fuzzy_search()
#             self.save_results(pattern, self.results)


    def fuzzy_word_search(self, pattern: str, limit: int, gap: int):
        """Search for 'pattern' with max 'gap' between any pairs of neighboring words in 'pattern' through all lyrics."""
        #set up the gui for threaded search
        self.update_progress_label(f"Searching for: '{pattern}'...")
        self.clear_lyrics()
        self.clear_results()
        self.reset_search()
        self.toggle_fuzzy_search()
        self.results = []
        self.cancel_flag = False
        self.index = 0
#         print(f"fuzzy_word_search(): pattern={pattern}, limit={limit}, gap={gap}")
#         print(f"{fuzzy_word_search.__name__}(), ")
        try:
            manager_thread = threading.Thread(target=self.fuzzy_manager, args=(pattern, limit, gap))
            manager_thread.start()
        except RuntimeError:
            logging.debug(f"RuntimeError, {word_search.__name__}(): pattern={pattern}")


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
            for i, artist, song, lyrics in db_util.index_search(self.index, self.step):
                if lyrics is not None and words is not None:
                    lyrics = lyrics.split(" ")
                    words = words.split(" ")
                    #TODO: remove punct from words and lyrics? 
                    answer = self.distant_neighboring_words(lyrics, words, gap)
                    return _gap_search_result(answer)
        return []


    def input_something_message(self) -> None:
        """Advises user to input something if they haven't."""
        messagebox.showinfo(title="Advice", message="Input something to begin a search.")


    def long_search_message(self) -> bool:
        """Displays 'yes/no' confirmation to user if the search may take a long time."""
        return messagebox.askyesno(title="Word or Phrase Search", message="This may take up to 30 minutes. You may continue to use the program to search while waiting. The word entry field and word gap option will be disabled until the search is completed. A notification will appear when the search is finished. Are you sure you want to continue?")


    #TODO, rethink FileMatch type
    def regex_search(self, data: Tuple[Text]) -> Optional[FileMatch]:
        """Perform a regex search for 'pattern'."""
        match = None
        try:
            match = self.regex.search(data[3])
            if match:
                return data[:3]
        except TypeError:
            logging.debug(f"TypeError: {file_}")
        self.tick_progress()
        print(data[0], end="\r")

    def save_results(string: Text, results: List) -> None:
        self.master.save_results(string, results)


    def search(self) -> None:
        """Perform database query.

        Possible Search Patterns (8):
            Artist  X   X   X   O   X   O   O   O
            Song    X   X   O   X   O   X   O   O
            Word    X   O   X   X   O   O   X   O
        """

        self.clear_results()
        self.clear_lyrics()

        artist = self.artist.get().strip()
        song = self.song.get().strip()
        grammar = self.words.get().strip()

        if self.fuzzy:
            self.fuzzy_search(Query(artist, song, grammar))
        else:
            self.exact_search(Query(artist, song, grammar))


    def show_results(self, songs: List[DisplayRecord]) -> None:
        self.master.show_results(songs)


    def stop(self) -> None:
        self.cancel_search()
        self.progress_bar.stop()
        self.search_in_progress = False
        self.cancel_flag = True
        self.index = 0


    @timing
    def thread_manager(self, limit: int, regex: re.Pattern):
        """Main search thread."""
        self.regex = regex
        self.cancel_flag = False
        results = set()
        files = db_util.all_artists_and_songs("songs")
        #iterate over db records

        with concurrent.futures.ThreadPoolExecutor(max_workers=5, thread_name_prefix=str(regex)) as executor:
            futures = {executor.submit(self.regex_search, file_) for file_ in files}
            for future in concurrent.futures.as_completed(futures):
                result = None
                try:
                    result = future.result()
                except TypeError as e:
                    logging.debug("TypeError: Threading...")
                if result is not None:
                    results.add(result)
                    self.results.append(result)
        result_count = len(self.results)
        self.stop()
#         self.update_progress_label(f"Search completed in {round(time_taken, 3)} minutes. {result_count} matches found.")
        self.toggle_fuzzy_search()
        records = [DisplayRecord(result[1], result[2]) for result in results]
        self.show_results(records)


    def tick_progress(self) -> None:
        self.progress_bar.step(1)


    def toggle_fuzzy_search(self) -> None:
        self.fuzzy = not self.fuzzy
        if self.fuzzy:
            self.words.state(["!disabled"])
            self.slider.state(["!disabled"])
        else:
            self.words.state(["disabled"])
            self.slider.state(["disabled"])


    def update_progress_label(self, string: Text) -> None:
        self.progress_label["text"] = string
        self.progress_bar["value"] = 0


    def update_scale(self, value):
        self.slider_var = value
        self.slider_label["text"] = f"Word gap: {int(float(value))}"


    def word_search(self, pattern: str, limit: int):
        """Search for 'pattern' in all lyrics."""
        #set up the gui for threaded search
        self.update_progress_label(f"Searching for: '{pattern}'...")
        self.clear_lyrics()
        self.clear_results()
        self.clear_search()
        self.toggle_fuzzy_search()
        regex = re.compile(pattern)
        self.results = []
        self.cancel_flag = False
        try:
            # create main thread to manage the other threads
            manager_thread = threading.Thread(target=self.thread_manager, args=(limit, regex))
            manager_thread.start()
        except RuntimeError:
            logging.debug(f"RuntimeError, {word_search.__name__}(): pattern={pattern}")
            #TODO, figure out the use of "from None" in exception handling to return just the most recent exception traceback
#         except Exception as e from None


