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

#Globals
regex_results = []
index = 0
cancel_flag = False


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


def handle_results_click(option: str) -> None:
    """Load the selected song's lyrics into the lyrics box."""
    index = list_results.curselection()
    selection = None
    try:
        selection = option.widget.get(index)
    except tk.TclError:
        pass

    artist = artist_search_entry.get().strip()
    song = song_search_entry.get().strip()
    result = None
    
    if selection:
        if artist and not song:
            result = artist_and_song(artist, selection)

        elif song and not artist:
            result = artist_and_song(selection, song)
        
        if result:
        #update the lyrics box
            lyrics_textbox.delete("1.0", tk.END)
            lyrics_textbox.insert("1.0", result)


def input_something_message() -> None:
    messagebox.showinfo(title="Advice", message="Input something to begin a search.")


def long_search_message() -> bool:
    message = messagebox.askyesno(title="Word or Phrase Search", message="This may take up to 30 minutes. You may continue to use the program to search while waiting. A notification will appear when the search is finished. Are you sure you want to continue?")
    return message


def regex_search(regex, index: int) -> None: 
    global regex_results

    cur, con = connect()
    cur.execute('SELECT * FROM songs WHERE id>=? AND id<=?', (index, index+100))
    records = cur.fetchall()

    for record in records:
        res = regex.search(record[3])
        if res:
            regex_results.append((record[0], record[1], record[2]))
    close_connection(cur, con)


def search() -> None:
    """Perform database query.

    Possible Search Patterns:
        Artist  X   X   X   O   X   O   O   O
        Song    X   X   O   X   O   X   O   O
        Word    X   O   X   X   O   O   X   O
    """

    # clear the listbox's contents
    list_results.delete(0, tk.END)

    a = artist_search_entry.get().strip()
    s = song_search_entry.get().strip()
    w = word_phrase_entry.get().strip()

    #wsa: if that song by that artist exists, then highlight its lyrics
    if w and s and a:
#         artists = song_query(s)
        print("TODO: Need to add highlighting to lyrics.")

    #ws : load the song, then highlight its lyrics
    elif w and s and not a:
        print("TODO: Need to add highlighting to lyrics.")
#         artists = song_query(s)

    #w a: load all the songs by the artist, then for each song highlight the matching words
    elif w and not s and a:
        print("TODO: Need to add highlighting to lyrics.")
#         artists = song_query(s)

    # sa: show lyrics for that song from that artist
    elif not w and s and a:
        result = artist_and_song(a, s)
        if result:
            lyrics_textbox.delete("1.0", tk.END)
            lyrics_textbox.insert("1.0", result)
        else:
            lyrics_textbox.delete("1.0", tk.END)
            list_results.delete(0, tk.END)
            list_results.insert(0, "No matching results.")

    #w  : search for all the lyrics that contain that word
    elif w and not s and not a:
        search_in_progress = cancel_btn["state"] is tk.NORMAL
        # if there is no search already running
        if search_in_progress:
            cancel = ask_to_cancel_search()
            if cancel:
                # then run a search
                message = long_search_message()
                if message:
                    word_search(w, records)
                    cancel_btn.config(state=tk.NORMAL)
        else:
            # then run a search
            message = long_search_message()
            if message:
                word_search(w, records)
                # set cancel on progress bar to enabled
                cancel_btn.config(state=tk.NORMAL)
                    


    # s : load all songs with that title
    elif not w and s and not a:
        songs = song_query(s)
        if len(songs) > 1:
            amt = 0
            for index, song in enumerate(sorted(songs, reverse=True)):
                list_results.insert(0, f'"{song[1]}" by {song[0]}')
                amt = index
        elif len(songs) == 1:
            for song in songs:
                list_results.insert(0, f'"{song[1]}" by {song[0]}')
        else:
            lyrics_textbox.delete("1.0", tk.END)
            list_results.delete(0, tk.END)
            list_results.insert(0, "No matching results.")

    #  a: load all songs written by that artist
    elif not w and not s and a:
        lyrics_textbox.delete("1.0", tk.END)
        songs = artist(a)
        list_results.delete(0, tk.END)
        amt = 0
        for index, song in enumerate(sorted(songs, reverse=True)):
            list_results.insert(0, song)
            amt = index

    #none, no input was given
    else:
        input_something_message()


def set_cancel_flag() -> None:
    """Set the quit flag to True."""
    global cancel_flag
    cancel_flag = True


def thread_manager(limit: int, regex: re.Pattern) -> None:
    global progress
    global index
    global cancel_flag
    step = 100

    start_time = time.time()

    # enable cancel button
    cancel_btn.config(state=tk.NORMAL)

    # ensure cancel_flag is false
    cancel_flag = False

    while index < limit and not cancel_flag:
        thread = threading.Thread(target=regex_search, args=(regex, index))
        thread.start()

        # wait for the thread to finish
        while thread.is_alive():
            continue

        thread.join()  # end the thread, (timeout=5) ? 
        index += step

        if progress.get() >= records:
            break

        progress_bar.step(step)

    #one last update, then exit
#     progress_bar.step(step)
    #TODO:reset progress bar color
    progress_bar.stop()
    progress_bar["value"] = 0

    # disable the cancel button
    cancel_btn.config(state=tk.DISABLED)

    # reset cancel_flag
    cancel_flag = False

    # let the user know the search is finished
    searching_for["text"] = f"Search complete. {len(regex_results)} matches found."
    
    # reset the index counter
    index = 0
#     print("regex results: ", regex_results)

    #TODO: show message that the search is finished and can be loaded into the current window, and saved into a file
    save = messagebox.askyesno(title="Save to File?", message="Would you like to save the results to a CSV file? You can reload the results into other programs like Excel.")
    if save:
        #show save dialog
        save_file = filedialog.asksaveasfilename()
        print("Saving to:", save_file)
        if save_file:
            with open(save_file, "w+") as f:
                writer = csv.writer(f, delimiter="|")
                writer.writerows(regex_results)
        print("Saved")
    end_time = time.time()
    print("Time taken:", (end_time - start_time) / 60, " minutes")


def word_search(pattern: str, limit: int):
    regex = re.compile(pattern)
    searching_for["text"] = f"Searching for: {pattern}"

    # clear lyrics text 
    lyrics_textbox.delete("1.0", tk.END)

    try:
        #create main thread to manage the other threads
        manager_thread = threading.Thread(target=thread_manager, args=(limit, regex))
        manager_thread.start()
    except RuntimeError:
        pass



def quit_gui() -> None:
    """Quit the program."""
    global cancel_flag
    #shut down any running threads
    cancel_flag = True
    # threads.join() ?
    quit()


if __name__ == "__main__":
    # load some simple stats
    records = record_count()
    artists = artist_count()

    frame_padding = {"padx": 10, "pady": 10}
    root_padding = {"padx": 5, "pady": 5}

    root = tk.Tk()
    width = 1000
    height = 600
    window_size = f"{width}x{height}"
    root.geometry(window_size)
    root_color = "#%02x%02x%02x" % (235, 235, 235)
    root.configure(bg=root_color)

    ################################################################################
    # DB records
    ################################################################################
    stats = ttk.LabelFrame(root, text="Stats")
    stats.pack(side=tk.TOP, fill=tk.X, **frame_padding)

    records_label = ttk.Label(stats, text="Songs:")
    records_label.pack(side=tk.LEFT)
    records_amt = ttk.Label(stats)
    records_amt.pack(side=tk.LEFT)

    artists_label = ttk.Label(stats, text="Artists:")
    artists_label.pack(side=tk.LEFT)
    artists_amt = ttk.Label(stats)
    artists_amt.pack(side=tk.LEFT)


    ################################################################################
    # Search Frame
    ################################################################################
    search_frame = ttk.LabelFrame(root, text="Search")
    search_frame.pack(side=tk.TOP, fill=tk.X, **frame_padding)

    # entryframe
    entry_frame = ttk.Frame(search_frame)
    entry_frame.pack(side=tk.LEFT)

    # options frame
    options_frame = ttk.Frame(search_frame)
    options_frame.pack(side=tk.LEFT)

    # row container
    artist_search = ttk.Frame(entry_frame)
    artist_search.pack(side=tk.TOP, fill=tk.X)
    artist_search_label = ttk.Label(artist_search, text="Artist:", width=15)
    artist_search_label.pack(side=tk.LEFT)
    artist_search_entry = ttk.Entry(artist_search, style="TEntry", width=40)
    artist_search_entry.pack(side=tk.LEFT)

    # row container
    song_search = ttk.Frame(entry_frame)
    song_search.pack(side=tk.TOP, fill=tk.X)
    song_search_label = ttk.Label(song_search, text="Song:", width=15)
    song_search_label.pack(side=tk.LEFT)
    song_search_entry = ttk.Entry(song_search, style="TEntry", width=40)
    song_search_entry.pack(side=tk.LEFT)

    word_search_frame = ttk.Frame(entry_frame)
    word_search_frame.pack(side=tk.TOP, fill=tk.X)
    word_phrase_label = ttk.Label(word_search_frame, text="Word or phrase:", width=15)
    word_phrase_label.pack(side=tk.LEFT)
    word_phrase_entry = ttk.Entry(word_search_frame, width=40)
    word_phrase_entry.pack(side=tk.LEFT)

    search_btn = ttk.Button(search_frame, text="Search Lyrics", command=search)
    search_btn.pack(side=tk.RIGHT)


    # radio button rows
    top_radio_frame = ttk.Frame(options_frame)
    top_radio_frame.pack(side=tk.TOP)
    middle_radio_frame = ttk.Frame(options_frame)
    middle_radio_frame.pack(side=tk.TOP)
    bottom_radio_frame = ttk.Frame(options_frame)
    bottom_radio_frame.pack(side=tk.TOP)

    # artist options
    artist_option_var = tk.StringVar()
    artist_option_exact = ttk.Radiobutton(top_radio_frame, text="Exact", variable=artist_option_var, value=1)
    artist_option_exact.pack(side=tk.LEFT)
    artist_option_fuzzy = ttk.Radiobutton(top_radio_frame, text="Fuzzy", variable=artist_option_var, value=2)
    artist_option_fuzzy.pack(side=tk.LEFT)

    # song options
    song_option_var = tk.StringVar()
    song_option_exact = ttk.Radiobutton(middle_radio_frame, text="Exact", variable=song_option_var, value=1)
    song_option_exact.pack(side=tk.LEFT)
    song_option_fuzzy = ttk.Radiobutton(middle_radio_frame, text="Fuzzy", variable=song_option_var, value=2)
    song_option_fuzzy.pack(side=tk.LEFT)

    # word options
    word_option_var = tk.StringVar()
    word_option_exact = ttk.Radiobutton(bottom_radio_frame, text="Exact", variable=word_option_var, value=1)
    word_option_exact.pack(side=tk.LEFT)
    word_option_fuzzy = ttk.Radiobutton(bottom_radio_frame, text="Fuzzy", variable=word_option_var, value=2)
    word_option_fuzzy.pack(side=tk.LEFT)



    ################################################################################
    # Search Results
    ################################################################################
    search_results_frame = ttk.LabelFrame(root, text="Results")
    search_results_frame.pack(fill=tk.BOTH, **frame_padding)
    search_results = ["Search for something"]
    list_items = tk.StringVar(value=search_results)

    list_results = tk.Listbox(search_results_frame, width=40, height=15, listvariable=list_items, selectmode=tk.SINGLE)
    list_results.bind("<<ListboxSelect>>", handle_results_click)
    list_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(list_results)
    scrollbar.config(command=list_results.yview)
    list_results.config(yscrollcommand=scrollbar.set)

    lyrics_textbox = tk.scrolledtext.ScrolledText(search_results_frame, height=20, width=60, wrap=tk.WORD)
    lyrics_textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


    ################################################################################
    # Progress Bar
    ################################################################################
    progress_footer = ttk.Frame(root)
    progress_footer.pack(side=tk.TOP)
    progress = tk.IntVar()
    progress_bar = ttk.Progressbar(progress_footer, length=width-100, maximum=records, mode="determinate", variable=progress)
    progress_bar.pack(side=tk.LEFT)
    cancel_btn = ttk.Button(progress_footer, text="Cancel", state=tk.DISABLED, command=set_cancel_flag)
    cancel_btn.pack(side=tk.RIGHT)

    # Regex Search Label
    searching_for = ttk.Label(root, text="Searching for:")
    searching_for.pack(side=tk.LEFT, **root_padding)

    # Quit button
    quit_btn = ttk.Button(root, text="Quit", command=quit_gui)
    quit_btn.pack(side=tk.RIGHT, **root_padding)

    # display simple stats
    records_amt["text"] = records
    artists_amt["text"] = artists

    # conveniences
    artist_search_entry.focus()

    root.mainloop()
