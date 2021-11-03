# std lib
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

# custom
# import db_util
from database import Database
from results import Results


FileMatch = namedtuple("FileMatch", ["file", "match"])
Query = namedtuple("Query", ["artist", "song", "grammar"])
DisplayRecord = namedtuple("DisplayRecord", ["artist", "song"])
DBRecord = namedtuple("DBRecord", ["id", "artist", "song", "lyrics"])
logging.basicConfig(filename='Logs/errors.log', encoding='utf-8', level=logging.DEBUG)

DATABASE = Database()

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
        self.db = DATABASE
        self.song_count = self.db.record_count()
        self.artist_count = self.db.artists()

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


    def ask_to_save(self, string: Text = None) -> bool:
        """Ask the user if they want to save the results."""

        return self.master.ask_to_save(string)


    def clear_search(self) -> None:
        """Clear the search entries."""

        self.words["text"] = " "
        self.song["text"] = " "
        self.artist["text"] = " "


    def cancel_search(self) -> bool:
        """Cancel the current search."""

        #TODO, possible circular ref with exact search GRAMMAR

        if self.search_in_progress:
            message = "Another search is currently in process.\
                    Do you wish to cancel that search and start a new one?"
            if messagebox.askyesno(title="Cancel Search", message=message):
                self.stop()
#         return message


    def clear_results(self) -> None:
        """Clear the results list."""

        self.master.clear_results()


    def clear_lyrics(self) -> None:
        """Clear the lyrics text box."""

        self.master.clear_lyrics()


    def disable_fuzzy_search(self) -> None:
        """Disable the fuzzy search options."""

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


    def enable_fuzzy_search(self) -> None:
        """Enable the fuzzy saerch options."""

        self.fuzzy = True
        self.slider.state(["!disabled"])


    def exact_all_three(self, query: Query) -> Tuple[DisplayRecord, Optional[Text]]:
        """Perform an exact search for all the query's paramaters."""

        lyrics = None
        record = self.db.artist_and_song(query.artist, query.song)
        match = re.search(query.grammar, record.lyrics)
        if match:
            records = DisplayRecord(record.artist, record.song)
            lyrics = record.lyrics
        else:
            records = DisplayRecord("", "")
        return records, lyrics
        #TODO: if any match, find all matches and highlight


    def exact_artist_song(self, query: Query) -> Tuple[DisplayRecord, Optional[Text]]:
        """Perform exact search for a song written by an artist."""

        lyrics = None
        record = self.db.artist_and_song(query.artist, query.song)
        if record:
            records = DisplayRecord(record.artist, record.song)
            lyrics = record.lyrics
        else:
            records = DisplayRecord("", "")
        return records, lyrics


    def exact_artist_grammar(self, query: Query) -> Tuple[List[DisplayRecord], Optional[Text]]:
        """Find exact grammar in all of the artist's songs."""

        lyrics = None
        records = self.db.songs_from_artist(query.artist)
        records = [DisplayRecord(record.artist, record.song) for record in records if re.search(query.grammar, record.lyrics)]
        if len(records) == 1:
            lyrics = records.lyrics
        if not records:
            records = [DisplayRecord("", "")]
        return records, lyrics


    def exact_song_grammar(self, query: Query) -> Tuple[List[DisplayRecord], Optional[Text]]:
        """Search for grammar within any song sharing the same name."""

        lyrics = None
        records = self.db.artists_having_song(query.song)
        if records:
            records = [DisplayRecord(record[1], record[2]) for record in records if re.search(query.grammar, record[3])]
#         else:
        if len(records) == 1:
            lyrics = records.lyrics
        if not records:
            records = [DisplayRecord("", "")]
        return records, lyrics


    def simple_re(self, record: DBRecord, query: Query) -> Optional[DisplayRecord]:
        """Simple regex search through record's lyrics for 'grammar'."""

        self.tick_progress()
        if re.search(query.grammar, record.lyrics):
            return DisplayRecord(record.artist, record.song)


    def exact_grammar(self, query: Query) -> None:
        """Find exact grammar in any song by any artist."""

        self.update_progress_label(f"Searching for: '{query.grammar}'...")
        self.clear_lyrics()
        self.clear_results()
        self.clear_search()
        self.toggle_fuzzy_search()
        pattern = re.compile(query.grammar)
        self.cancel_flag = False

        results = set()
        limit = self.song_count
        records = self.db.all_records()

        for index, record in enumerate(records):
            match = pattern.search(record.lyrics)
            if match:
                results.add(DisplayRecord(record.artist, record.song))
            print("Progress:", index, end="\r")

        #TODO, log search params and results
        print()
        print("results:", len(results))
        results = list(results)
#         results.sort(reverse=True)
        return results


    def exact_song(self, query: Query) -> Tuple[List[DisplayRecord], Optional[Text]]:
        """Search for all songs that share the same name."""

        lyrics = None
        records = self.db.artists_having_song(query.song)
        if not records:
            records = [DisplayRecord("", "")]
        elif len(records) == 1:
            lyrics = records.lyrics
            records = DisplayRecord(records.artist, records.song)
        else:
            records = [DisplayRecord(record.artist, record.song) for record in records]
        return records, lyrics


    def exact_artist(self, query: Query) -> Tuple[List[DisplayRecord], Optional[Text]]:
        """Search for all songs written by one artist."""

        lyrics = None
        records = self.db.songs_from_artist(query.artist)
        if not records:
            records = [DisplayRecord("", "")]
        elif len(records) == 1:
            lyrics = records.lyrics
            records = DisplayRecord(records.artist, records.song)
        else:
            records = [DisplayRecord(record.artist, record.song) for record in records]
        return records, lyrics


    def exact_search(self, query: Query) -> Tuple[List[DisplayRecord], Optional[Text]]:
        """Perform an exact search on 'query'."""

        artist = query.artist
        song = query.song
        grammar = query.grammar
        lyrics = None
        records = None

        if artist and song and grammar:
            records, lyrics = self.exact_all_three(query)

        elif artist and song and not grammar:
            records, lyrics = self.exact_artist_song(query)

        elif artist and not song and grammar:
            records, lyrics = self.exact_artist_grammar(query)
#             if self.ask_to_save():
#                 self.save_results(records)

        elif not artist and song and grammar:
            records, lyrics = self.exact_song_grammar(query)

        elif not artist and not song and grammar:
            records = self.exact_grammar(query)
#             records = DisplayRecord("Searching...", "")

        elif not artist and song and not grammar:
            records, lyrics = self.exact_song(query)

        elif artist and not song and not grammar:
            records, lyrics = self.exact_artist(query)

        else:
            self.input_something_message()

        return records, lyrics


    def fuzzy_search(self, query: Query) -> Tuple[List[DisplayRecord], Optional[Text]]:
        """Perform a fuzzy search."""

        artist = query.artist
        song = query.song
        grammar = query.grammar
        lyrics = None
        records = None
        word_gap = self.slider.get()

        #ARTIST     SONG    GRAMMAR
        if artist and song and grammar:
            lyrics = db_uitl.fuzzy_artist_and_song(artist, song)

        #ARTIST     SONG
        elif artist and song and not grammar:
            lyrics = db_uitl.fuzzy_artist_and_song(artist, song)

        #ARTIST             GRAMMAR
        elif artist and not song and grammar:
            #doesn't make sense
            artists = self.db.fuzzy_song(song)

        #           SONG    GRAMMAR
        elif not artist and song and grammar:
            artists = self.db.fuzzy_song(song)

        #                   GRAMMAR
        elif not artist and not song and grammar:
            gap = self.slider.get()
            self.fuzzy_word_search(grammar, self.song_count, gap)

        #           SONG
        elif not artist and song and not grammar:
            artists = self.db.fuzzy_song("Databases/lyrics.db", "songs", song)

        #ARTIST
        elif artist and not song and not grammar:
            songs = self.db.fuzzy_songs_from_artist(artist)
#             records = [DisplayRecord(records[0], records[1]) for records in records]

        #NONE     NONE    NONE
        else:
            self.input_something_message()

        return records, lyrics


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
            self.stop()
            self.update_progress_label(f"Search completed in {round(time_taken, 3)} minutes. {result_count} matches found.")
            self.toggle_fuzzy_search()
            #TODO, return results


    def fuzzy_word_search(self, pattern: Text, limit: int, gap: int):
        """Search for 'pattern' with max 'gap' between any pairs of neighboring words in 'pattern' through all lyrics."""

        #set up the gui for threaded search
        self.update_progress_label(f"Searching for: '{pattern}'...")
        self.clear_lyrics()
        self.clear_results()
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
            logging.debug(f"RuntimeError, {fuzzy_word_search.__name__}(): pattern={pattern}")
        #TODO, return results

    def gap_search(self, words: Text="", gap: int=0) -> List:
        """Searches for all 'words' with max 'gap' between any neighboring pair of words."""
        #TODO, define return type, use namedtuple


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
            for i, artist, song, lyrics in self.db.index_search(self.index, self.step):
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
        
        message = "Complex searches may take up to 10 minutes.\
                You may continue to use the program to search while waiting.\
                The word entry field and word gap option will be\
                disabled until the search is completed.\
                A notification will appear when the search is finished.\
                Are you sure you want to continue?"
        return messagebox.askyesno(title="Word or Phrase Search", message=message)


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
#         print(data[0], end="\r")
        #TODO, add return statement


    def save_results(self, results: List[DisplayRecord]) -> None:
        """Save the results"""

        self.master.save_results(results)


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
        records = None
        lyrics = None

        if self.fuzzy:
            self.fuzzy_search(Query(artist, song, grammar))
        else:
            records, lyrics = self.exact_search(Query(artist, song, grammar))
        self.show_results(records, lyrics=lyrics)


    def show_results(self, records: List[DisplayRecord], lyrics=None) -> None:
        self.master.show_results(records, lyrics)


    def stop(self) -> None:
        self.cancel_search()
        self.progress_bar.stop()
        self.search_in_progress = False
        self.cancel_flag = True
        self.index = 0


    @timing
    def old_thread_manager(self, limit: int, regex: re.Pattern):
        """Main search thread."""

        self.regex = regex
        self.cancel_flag = False
        results = set()
        records = self.db.all_records()
        #iterate over db records

        with concurrent.futures.ThreadPoolExecutor(max_workers=5, thread_name_prefix=str(regex)) as executor:
            futures = {executor.submit(self.regex_search, record) for record in records}
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

        #TODO, return results instead of calling show
        self.show_results(records)


    def tick_progress(self) -> None:
        self.progress_bar.step(1)


    def toggle_fuzzy_search(self) -> None:
        """Toggle the fuzzy search options."""

        self.fuzzy = not self.fuzzy
        if self.fuzzy:
            self.words.state(["!disabled"])
            self.slider.state(["!disabled"])
        else:
            self.words.state(["disabled"])
            self.slider.state(["disabled"])


    def update_progress_label(self, string: Text) -> None:
        """Update the progress bar label with new text."""

        self.progress_label["text"] = string
        self.progress_bar["value"] = 0


    def update_scale(self, value):
        """Update the scale label value with new text."""

        self.slider_var = value
        self.slider_label["text"] = f"Word gap: {int(float(value))}"
