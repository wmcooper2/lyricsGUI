#std lib
from pathlib import Path
import sqlite3
import time
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import scrolledtext


# custom
from db_util import *

#Globals
regex_results = []
index = 0
cancel_flag = False


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
    """Perform database query."""

    # clear the listbox's contents
    list_results.delete(0, tk.END)

    a = artist_search_entry.get().strip()
    s = song_search_entry.get().strip()
    w = word_phrase_entry.get().strip()

    #possible patterns
    #wsa    
    #ws     
    #w a    
    # sa    
    #w      
    # s     
    #  a    
    #none   


    #wsa
    if w and s and a:
        # ask if the user wants to cancel the current word search
        pass
        # load the one song
        artists = song_query(s)
        # highlight the locations within the lyrics box where the regex matches

    #ws
    elif w and s and not a:
        # ask if the user wants to cancel the current word search
        pass
        # load all songs that have that song name
        artists = song_query(s)
        # then when they are clicked on in the list box
            # highlight the locations in the lyrics box where the regex matches

    #w a
    elif w and not s and a:
        # ask if the user wants to cancel the current word search
        pass
        # load all the songs by the artist, then do the same as with "ws " option

    # sa
    elif not w and s and a:
        #show lyrics for that song from that artist
        result = artist_and_song(a, s)
        if result:
            lyrics_textbox.delete("1.0", tk.END)
            lyrics_textbox.insert("1.0", result)
        else:
            lyrics_textbox.delete("1.0", tk.END)
            list_results.delete(0, tk.END)
            list_results.insert(0, "No matching results.")

    #w
    elif w and not s and not a:
        # if there is a current word search, ask if the user wants to cancel it.
        # search for any song from any artist that contains the pattern
        message = long_search_message()
        if message:
            word_search(w, records)
            # set cancel on progress bar to enabled

    # s
    elif not w and s and not a:
        # load all songs with that title
        artists = song_query(s)
#         list_results.delete(0, tk.END)
        if len(artists) > 1:
            amt = 0
            for index, song in enumerate(sorted(artists, reverse=True)):
                list_results.insert(0, song)
                amt = index
        elif len(artists) == 1:
            pass
            #TODO: tell user there is only one artist
        else:
            pass
            #TODO: tell user there are no results

    #  a
    elif not w and not s and a:
        # load all songs written by that artist
        lyrics_textbox.delete("1.0", tk.END)
        songs = artist(a)
        list_results.delete(0, tk.END)
        amt = 0
        for index, song in enumerate(sorted(songs, reverse=True)):
            list_results.insert(0, song)
            amt = index

    #none
    else:
        # show a message that says you need to input something
        print("input something first...")
        input_something_message()


def set_cancel_flag() -> None:
    """Set the quit flag to True."""
    global cancel_flag
    cancel_flag = False


def thread_manager(limit: int, regex: re.Pattern) -> None:
    global progress
    global index
    global cancel_flag
    step = 100

    # enable cancel button
    cancel_btn.config(state=tk.NORMAL)

    # ensure cancel_flag is false
    cancel_flag = False

    while index < limit:
        thread = threading.Thread(target=regex_search, args=(regex, index))
        thread.start()

        # wait for the thread to finish
        while thread.is_alive() and not cancel_flag:
            continue

        thread.join()  # end the thread, (timeout=5) ? 
        index += step

        if progress.get() >= records:
            break

        progress_bar.step(step)

    #one last update, then exit
    progress_bar.step(step)

    # disable the cancel button
    cancel_btn.config(state=tk.DISABLE)

    # reset cancel_flag
    cancel_flag = False
    
    # reset the index counter
    index = 0
#     print("regex results: ", regex_results)
#     show message that the search is finished and can be loaded into the current window, and saved into a file


def word_search(pattern: str, limit: int):
    regex = re.compile(pattern)

    #create main thread to manage the other threads
    manager_thread = threading.Thread(target=thread_manager, args=(limit, regex))
    manager_thread.start()


def quit_gui() -> None:
    """Quit the program."""
    global cancel_flag
    #shut down any running threads
    cancel_flag = True
    # threads.join() ?

#     cur.close()
#     con.close()
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

    records_label = ttk.Label(stats, text="Records:")
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

    # row container
    artist_search = ttk.Frame(search_frame)
    artist_search.pack(side=tk.TOP, fill=tk.X)
    artist_search_label = ttk.Label(artist_search, text="Artist:", width=15)
    artist_search_label.pack(side=tk.LEFT)
    artist_search_entry = ttk.Entry(artist_search, style="TEntry", width=40)
    artist_search_entry.pack(side=tk.LEFT)

    # row container
    song_search = ttk.Frame(search_frame)
    song_search.pack(side=tk.TOP, fill=tk.X)
    song_search_label = ttk.Label(song_search, text="Song:", width=15)
    song_search_label.pack(side=tk.LEFT)
    song_search_entry = ttk.Entry(song_search, style="TEntry", width=40)
    song_search_entry.pack(side=tk.LEFT)

    word_search_frame = ttk.Frame(search_frame)
    word_search_frame.pack(side=tk.TOP, fill=tk.X)
    word_phrase_label = ttk.Label(word_search_frame, text="Word or phrase:", width=15)
    word_phrase_label.pack(side=tk.LEFT)
    word_phrase_entry = ttk.Entry(word_search_frame, width=40)
    word_phrase_entry.pack(side=tk.LEFT)

    search_btn = ttk.Button(search_frame, text="Search Lyrics", command=search)
    search_btn.pack(side=tk.RIGHT)


    ################################################################################
    # Search Results
    ################################################################################
    search_results_frame = ttk.LabelFrame(root, text="Results")
    search_results_frame.pack(fill=tk.BOTH, **frame_padding)
#     search_results_frame.configure(bd=2, bg=root_color)
    search_results = ["Search for something"]
    list_items = tk.StringVar(value=search_results)

    list_results = tk.Listbox(search_results_frame, width=40, height=15, listvariable=list_items, selectmode=tk.SINGLE)
#     list_results = tk.scrolledtext.ScrolledText(search_results_frame, height=15)
    list_results.bind("<<ListboxSelect>>", handle_results_click)
    list_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(list_results)
    scrollbar.config(command=list_results.yview)
    list_results.config(yscrollcommand=scrollbar.set)

    lyrics_textbox = tk.scrolledtext.ScrolledText(search_results_frame, height=20, width=60, wrap=tk.WORD)
    lyrics_textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


    ################################################################################
    # Footer
    ################################################################################
    footer = ttk.Frame(root)
    footer.pack(side=tk.TOP)
    progress = tk.IntVar()
    progress_bar = ttk.Progressbar(footer, length=width-100, maximum=records, mode="determinate", variable=progress)
    progress_bar.pack(side=tk.LEFT)
    cancel_btn = ttk.Button(footer, text="Cancel", state=tk.DISABLED, command=set_cancel_flag)
    cancel_btn.pack(side=tk.RIGHT)


    # Quit button
    quit_btn = ttk.Button(root, text="Quit", command=quit_gui)
    quit_btn.pack(side=tk.RIGHT, **root_padding)

    # display simple stats
    records_amt["text"] = records
    artists_amt["text"] = artists

    # conveniences
    artist_search_entry.focus()

    root.mainloop()
