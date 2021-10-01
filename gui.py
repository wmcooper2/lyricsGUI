#std lib
import logging
import tkinter as tk
from tkinter import ttk

#custom
from results import Results
from lyricstab import LyricsTab
from youtubetab import YouTubeTab

logging.basicConfig(filename='errors.log', encoding='utf-8', level=logging.DEBUG)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.LEFT, expand=True)
        self.lyrics_tab = LyricsTab(self.notebook)
#         self.youtube_tab = YouTubeTab(self.notebook)
        self.notebook.add(self.lyrics_tab, text="Lyrics")
#         self.notebook.add(self.youtube_tab, text="YouTube")


if __name__ == "__main__":
    frame_padding = {"padx": 10, "pady": 10}
    root_padding = {"padx": 5, "pady": 5}

    app = App()
    app_width = 1000
    app_height = 700
    app_xpos = 100
    app_ypos = 100
    app_window_size = f"{app_width}x{app_height}+{app_xpos}+{app_ypos}"
    app.geometry(app_window_size)
    app_color = "#%02x%02x%02x" % (235, 235, 235)
    app.configure(bg=app_color)
    app.mainloop()
