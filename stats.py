import tkinter as tk
from tkinter import ttk

def count_files(dir_: str) -> None:
    """Count all files in dir_."""
    count_btn["text"] = "Counting..."
    for index, file_ in enumerate(Path(dir_).iterdir()):
        if file_.is_file():
            file_amt["text"] = str(index)
            root.update()
    count_btn["text"] = "Count Files"
    root.update()



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


