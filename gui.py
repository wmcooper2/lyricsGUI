#std lib
from pathlib import Path
import tkinter as tk
from tkinter import ttk

#3rd party
import psycopg2

# custom
from db_util import *

# Database
# DB; "dbname=lyricsdemo user=postgres"
con = psycopg2.connect("dbname=lyricsdemo user=postgres")
cur = con.cursor()

root = tk.Tk()
root.geometry("600x600")
# root.configure(bg="blue")
# tk_rgb = "#%02x%02x%02x" % (128, 192, 200)
root_color = "#%02x%02x%02x" % (235, 235, 235)
root.configure(bg=root_color)

# paddings = {"padx": 10, "pady": 10}
s = ttk.Style()
s.configure(".", background="green")
s.configure("TButton", background="white")
s.configure("TEntry", background="white")




# delete?
def count_files(dir_: str) -> None:
    """Count all files in dir_."""
    count_btn["text"] = "Counting..."
    for index, file_ in enumerate(Path(dir_).iterdir()):
        if file_.is_file():
            file_amt["text"] = str(index)
            root.update()
    count_btn["text"] = "Count Files"
    root.update()

def count_artists() -> None:
    artists_amt["text"] = artist_count()

def count_records() -> None:
#     records = record_count()
    records_amt["text"] = record_count()
    # update record count

def search() -> None:
    """Perform database query."""
    a = artist_search_entry.get().strip()
    s = song_search_entry.get().strip()

    if a and s:
        #search for artist with song
        #if found, show lyrics for that song from that artist
        print("artist and song")
    elif a:
        #only artist, if found, show song names
        songs = artist(a)
        list_results.delete(0, tk.END)
        for song in songs:
            list_results.insert(0, song)
        search_results_frame["text"] = f"Songs by {a}"

    elif s:
        #only song
        artists = song_query(s)
        list_results.delete(0, tk.END)
        # if more than one, show a list of song
        if len(artists) > 1:
            for song in artists:
                list_results.insert(0, song)
                search_results_frame["text"] = "Multiple artists..."
        elif len(artists) == 1:
            search_results_frame["text"] = "Only one match"

        else:
            list_results.insert(0, song)
            search_results_frame["text"] = "No matches"
    else:
        #message that says you need to input something
        print("input something first...")

#     add results to list_results
#     .update()






def quit_gui() -> None:
    """Quit the program."""
    cur.close()
    con.close()
    quit()





################################################################################
# Files
################################################################################
count_btn = ttk.Button(root, text="Count Files", command=lambda: count_files("Databases/data9"), style="TButton")
count_btn.grid(row=9, column=0, sticky=tk.W)

# file count = 38520
# progress_bar = ttk.Progressbar(root, length=100, mode="indeterminate", orient=tk.HORIZONTAL)
# progress_bar.grid(row=0, column=1)

file_amt = ttk.Label(root)
file_amt.grid(row=1, column=2, sticky=tk.E)


################################################################################
# DB records
################################################################################
stats = tk.LabelFrame(root, text="DB Stats")
stats.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
stats.configure(bg=root_color, bd=2)

records_label = ttk.Label(stats, text="Records:")
records_label.grid(row=1, column=0, sticky=tk.W)
records_amt = ttk.Label(stats)
records_amt.grid(row=1, column=1, sticky=tk.E)


artists_label = ttk.Label(stats, text="Artists:")
artists_label.grid(row=2, column=0, sticky=tk.W)
artists_amt = ttk.Label(stats)
artists_amt.grid(row=2, column=1, sticky=tk.E)



################################################################################
# DB search
################################################################################
search_frame = tk.LabelFrame(root, text="Search")
search_frame.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
search_frame.configure(bg=root_color, bd=2)

artist_search_label = ttk.Label(search_frame, text="Artist:")
artist_search_label.grid(row=0, column=0, sticky=tk.W)

artist_search_entry = ttk.Entry(search_frame, style="TEntry")
artist_search_entry.grid(row=0, column=1, sticky=tk.E)

song_search_label = ttk.Label(search_frame, text="Song:")
song_search_label.grid(row=1, column=0, sticky=tk.W)

song_search_entry = ttk.Entry(search_frame)
song_search_entry.grid(row=1, column=1, sticky=tk.E)

search_btn = ttk.Button(search_frame, text="Search", command=search)
search_btn.grid(row=2, column=0, sticky=tk.W)


################################################################################
# Search Results
################################################################################
search_results_frame = tk.LabelFrame(search_frame, text="Results")
search_results_frame.grid(row=9, column=0, sticky=tk.W, columnspan=2, padx=10, pady=10)
search_results_frame.configure(bd=2, bg=root_color)

search_results = ["Search for something"]
list_items = tk.StringVar(value=search_results)

list_results = tk.Listbox(search_results_frame, height=15, listvariable=list_items)
list_results.grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
# scrollbar = tk.Scrollbar(list_results)
# scrollbar.config(command=list_results.yview)
# list_results.config(yscrollcommand=scrollbar.set)






# Quit button
quit_btn = ttk.Button(root, text="Quit", command=quit_gui)
quit_btn.grid(row=10, column=0, sticky=tk.SW)


if __name__ == "__main__":
    count_records()
    count_artists()
    # main
    root.mainloop()
