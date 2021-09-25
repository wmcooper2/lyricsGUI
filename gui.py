#std lib
import csv
from pathlib import Path
import sqlite3
import time
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import scrolledtext


# custom
from db_util import *


def ask_to_cancel_search() -> bool:
    message = messagebox.askyesno(title="Cancel Current Search", message="Another search is currently in process. Do you wish to cancel that search and start a new one?")


def count_files(dir_: str) -> None:
    """Count all files in dir_."""
    count_btn["text"] = "Counting..."
    for index, file_ in enumerate(Path(dir_).iterdir()):
        if file_.is_file():
            file_amt["text"] = str(index)
            root.update()
    count_btn["text"] = "Count Files"
    root.update()


def input_something_message() -> None:
    messagebox.showinfo(title="Advice", message="Input something to begin a search.")


def long_search_message() -> bool:
    message = messagebox.askyesno(title="Word or Phrase Search", message="This may take up to 30 minutes. You may continue to use the program to search while waiting. A notification will appear when the search is finished. Are you sure you want to continue?")
    return message


class Stats(tk.Frame):
    def __init__(self, master):
        super().__init__()
        self.root = ttk.LabelFrame(master, text="Stats")
        self.root.grid(row=0, column=0, sticky=tk.W)

        self.records_label = ttk.Label(self.root, text="Songs:")
        self.records_label.grid(row=0, column=0)
        self.records_amt = ttk.Label(self.root, text="Loading...")
        self.records_amt.grid(row=0, column=1)

        self.artists_label = ttk.Label(self.root, text="Artists:")
        self.artists_label.grid(row=0, column=3)
        self.artists_amt = ttk.Label(self.root, text="Loading...")
        self.artists_amt.grid(row=0, column=4)


class Search(tk.Frame):
    def __init__(self, master):
        super().__init__()
        
        self.fuzzy = False
        self.song_count = record_count()
        self.artist_count = artist_count()

        self.root = ttk.LabelFrame(master, text="Search")
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
        self.button = ttk.Button(self.root, text="Search", command=master.search)
        self.button.grid(row=2, column=10, columnspan=10)

        self.progress = tk.IntVar()
        self.progress_label = ttk.Label(self.root, text="Searching for: Nothing yet...")
        self.progress_label.configure(font="Helvetica 12 italic")
        self.progress_label.grid(row=1, column=0, sticky=tk.W, padx=10)
        self.progress_bar = ttk.Progressbar(self.root, length=800, maximum=self.song_count, mode="determinate", variable=self.progress)
        self.progress_bar.grid(row=2, column=0, columnspan=9)

    def update_scale(self, value):
        self.slider_var = value
        self.slider_label["text"] = f"Word gap: {int(float(value))}"

    def disable_fuzzy_search(self):
        self.fuzzy = False
        self.slider.state(["disabled"])

    def enable_fuzzy_search(self):
        self.fuzzy = True
        self.slider.state(["!disabled"])
        

class Results(tk.Frame):
    def __init__(self, master):
        super().__init__()
#         self.root = ttk.LabelFrame(master, text="Results")
        self.root = ttk.LabelFrame(master)
        self.root.grid(row=2, column=0, sticky=tk.E+tk.W)
        self.root.grid_columnconfigure(0, weight=1)  # allows expansion of columns and rows?

        # TODO:text results frame

        self.search_results = ["Search results appear here."]
        self.list_items = tk.StringVar(value=self.search_results)

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
        self.lyrics.grid(row=0, column=0, sticky=tk.E+tk.W+tk.N+tk.S, padx=5, pady=5)
        self.lyrics.tag_configure("highlight", background="yellow", foreground="black")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.LEFT, expand=True)
        self.lyrics_tab = LyricsTab(self.notebook)
        self.youtube_tab = YouTubeTab(self.notebook)
        self.notebook.add(self.lyrics_tab, text="Lyrics")
        self.notebook.add(self.youtube_tab, text="YouTube")

class YouTubeTab(tk.Frame):
    def __init__(self, master):
        super().__init__()

class LyricsTab(tk.Frame):
    def __init__(self, master):
        super().__init__()
#         self.stats = Stats(self)
#         # display simple stats
#         self.stats.records_amt["text"] = self.records
#         self.stats.artists_amt["text"] = self.artist_count

        #TODO: thread to load stats

        self.search = Search(self)
        self.results = Results(self)

        self.regex_results = []
        self.index = 0
        self.step = 100
#         self.fuzzy = False


        # conveniences
        self.search.artist.focus()

        # Quit button
        #TODO: add styling to fix the quit button?
#         self.style = ttk.Style()
#         self.style.configure("My.TButton", background="blue")
#         self.quit_btn = ttk.Button(self, text="Quit", command=self.quit_gui, style="My.TButton")
        self.quit_btn = ttk.Button(self, text="Quit", command=self.quit_gui)
        self.quit_btn.grid(row=3, column=0, columnspan=10, sticky=tk.E+tk.W)
        self.quit_btn.grid_columnconfigure(0, weight=1)  # allows expansion of columns and rows?


    def handle_results_click(self, option: str) -> None:
        """Load the selected song's lyrics into the lyrics box."""
        selection = None
        index = self.results.list_.curselection()
        try:
            selection = option.widget.get(index)
        except tk.TclError:
            #TODO:?
            pass

        song = None
        artist = None
        if selection:
            song_match = re.match('\".*?\"', selection)
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


    def regex_search(self, pattern) -> None: 
        """Perform a regex search for 'pattern'."""
        records = index_search(self.index, self.step)
        for record in records:
            match = pattern.search(record[3])
            if match:
                self.regex_results.append((record[0], record[1], record[2]))


    def search(self) -> None:
        """Perform database query.

        Possible Search Patterns:
            Artist  X   X   X   O   X   O   O   O
            Song    X   X   O   X   O   X   O   O
            Word    X   O   X   X   O   O   X   O

        Personal note:
        Completed?
            Fuzzy   O       O   O           O   O
            Exact   O   O   O   O           O
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
                match = re.search(w, lyrics)
                self.highlight_lyrics(lyrics, words)
            self.show_lyrics(lyrics)
            self.show_songs([(a, s)])

        #ws : load the song, then highlight its lyrics
        elif w and s and not a:
            if fuzzy:
                #find all songs that are similar
                artists = fuzzy_song_query(s)
                #TODO: ...then tag the lyrics

        #TODO: this one might be a little more involved...
        #w a: load all the songs by the artist, then for each song highlight the matching words
        elif w and not s and a:
            if fuzzy:
                #find all artists that are similar
                artists = fuzzy_song_query(s)

                #just load all the songs by the artist.
                #when a song is clicked, grab the lyrics from the DB and add tags on the spot

            else:
                artists = song_query(s)
                #just load all the songs by the artist.
                #when a song is clicked, grab the lyrics from the DB and add tags on the spot

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
            #TODO: implement a word gap fuzzy lookup
#             if fuzzy:
            #TODO: decide on whether or not to give user the cancel ability and how to implement
            search_in_progress = self.search.button["text"] != "Search"
            # if there is no search already running
            if search_in_progress:
                cancel = ask_to_cancel_search()
                if cancel:
                    # then run a search
                    message = long_search_message()
                    if message:
                        self.word_search(w, self.song_count)
            else:
                # then run a search
                message = long_search_message()
                if message:
                    self.word_search(w, self.search.song_count)

        # s : load all songs with that title
        elif not w and s and not a:
            if fuzzy:
                songs = fuzzy_song_query(s)
            else:
                songs = song_query(s)
            self.show_songs(songs)

        #  a: load all songs written by that artist
        elif not w and not s and a:
            if fuzzy:
                songs = fuzzy_artist(a)
            else:
                songs = artist2(a)
            self.show_songs(songs)

        #none, no input was given
        else:
            input_something_message()


    def clear_results(self) -> None:
        """Delete contents of artist/song listbox and lyrics text box."""
        self.results.list_.delete(0, tk.END)
        self.results.lyrics.delete("1.0", tk.END)


    def show_songs(self, data) -> None:
        """Load the song/artist results into the list box."""
        box = self.results.list_
        self.clear_results()
        if len(data) > 1:
            for index, record in enumerate(sorted(data, reverse=True)):
                song, artist = record[1].title(), record[0].title()
                self.results.list_.insert(0, f'"{song}" by {artist}')
        elif len(data) == 1:
            self.results.list_.delete(0, tk.END)
            song, artist = data[0][1].title(), data[0][0].title()
            self.results.list_.insert(0, f'"{song}" by {artist}')
            lyrics = artist_and_song(artist, song)
            self.show_lyrics(lyrics)
        else:
            box.insert(0, "No matching results.")


    def show_lyrics(self, data) -> None:
        """Load the lyrics results into the text box."""
        box = self.results.lyrics
        if data:
            box.delete("1.0", tk.END)
            box.insert("1.0", data)
        else:
            box.delete("1.0", tk.END)
            box.delete("1.0", tk.END)
            box.insert("1.0", "No matching results.")


    def thread_manager(self, limit: int, pattern: str) -> None:
        """Main search thread."""
        regex = re.compile(pattern)
        self.search.progress_label["text"] = f"Searching for: '{pattern}'..."
        self.clear_results()
        start_time = time.time()
        self.cancel_flag = False
        self.regex_results = []

        # disable the word entry
        self.search.words.state(["disabled"])

        # disable the scale
        self.search.slider.state(["disabled"])

        #TODO set search button to cancel and toggle its functionality?
        while self.index < limit and not self.cancel_flag:
            thread = threading.Thread(target=self.regex_search, args=(regex,))
            thread.start()

            # wait for the thread to finish
            while thread.is_alive():
                continue

            thread.join()  # end the thread, (timeout=5) ? 
            self.index += self.step

            if self.search.progress.get() >= self.search.song_count:
                break

            self.search.progress_bar.step(self.step)

        #one last update, then exit
        #TODO:reset progress bar color
        self.search.progress_bar.stop()
        self.search.progress_bar["value"] = 0

        # reset cancel_flag
        self.cancel_flag = False

        result_count = len(self.regex_results)
        # let the user know the search is finished
        self.search.progress_label["text"] = f"Search complete. {result_count} matches found."
        
        # reset the index counter
        self.index = 0

        # enable the word entry
        self.search.words.state(["!disabled"])

        # enable the scale
        self.search.slider.state(["!disabled"])


        save = messagebox.askyesno(title="Save to File?", message=f"Search for {pattern} is complete. Would you like to save the results to a CSV file? You can reload the results into other programs like Excel.\n\nThe word entry field and word gap option will be disabled until the search is completed.")
        if save:
            #show save dialog
            save_file = filedialog.asksaveasfilename()
            if save_file:
                with open(save_file, "w+") as f:
                    writer = csv.writer(f, delimiter="|")
                    writer.writerows(self.regex_results)
        end_time = time.time()
        print("Time taken:", (end_time - start_time) / 60, " minutes")

        #TODO: show message that the search is finished and can be loaded into the current window, and saved into a file
        if result_count > 100:
            view_now = messagebox.askyesno(title="Save to File?", message=f"There are {result_count} results. Do you want to view all of them now?")
            if view_now:
                artist_songs = [(record[1], record[2])for record in self.regex_results]
                self.show_songs(artist_songs)


    def word_search(self, pattern: str, limit: int):
        """Search for 'pattern' in all lyrics."""
        try:
            # create main thread to manage the other threads
            manager_thread = threading.Thread(target=self.thread_manager, args=(limit, pattern))
            manager_thread.start()
        except RuntimeError:
            pass

    def quit_gui(self) -> None:
        """Quit the program."""
        #shut down any running threads
        self.cancel_flag = True

        # threads.join() ?
        quit()







if __name__ == "__main__":
    frame_padding = {"padx": 10, "pady": 10}
    root_padding = {"padx": 5, "pady": 5}

    app = App()
    app_width = 1000
    app_height = 700
    app_window_size = f"{app_width}x{app_height}"
    app.geometry(app_window_size)
    app_color = "#%02x%02x%02x" % (235, 235, 235)
    app.configure(bg=app_color)
    app.mainloop()
