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



def quit_gui() -> None:
    """Quit the program."""
    cur.close()
    con.close()
    quit()





################################################################################
# Files
################################################################################
stats = tk.Frame(root)
# s = ttk.Style()
s.configure("TButton", background="white")
count_btn = ttk.Button(stats, text="Count Files", command=lambda: count_files("Databases/data9"), style="TButton")
count_btn.grid(row=0, column=0, sticky=tk.W)

# file count = 38520
# progress_bar = ttk.Progressbar(stats, length=100, mode="indeterminate", orient=tk.HORIZONTAL)
# progress_bar.grid(row=0, column=1)

file_amt = ttk.Label(stats)
file_amt.grid(row=0, column=2)


################################################################################
# DB records
################################################################################
records_label = ttk.Label(stats, text="Records:")
records_label.grid(row=1, column=0, sticky=tk.W)
records_amt = ttk.Label(stats)
records_amt.grid(row=1, column=1, sticky=tk.E)


artists_label = ttk.Label(stats, text="Artists:")
artists_label.grid(row=2, column=0, sticky=tk.W)
artists_amt = ttk.Label(stats)
artists_amt.grid(row=2, column=1, sticky=tk.E)

# Quit button
quit_btn = ttk.Button(root, text="Quit", command=quit_gui)
quit_btn.grid(row=10, column=0, sticky=tk.W)


if __name__ == "__main__":
    count_records()
    count_artists()
    # main
    root.mainloop()
