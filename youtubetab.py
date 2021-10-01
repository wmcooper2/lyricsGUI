import tkinter as tk
from tkinter import ttk


class YouTubeTab(tk.Frame):
    def __init__(self, master):
        super().__init__()
        
        #TODO, try to figure out how best to display the lyrics for the song and the video frame
        # song/artist results
#         self.artist_song_results_frame = ttk.LabelFrame(self, text="Songs by Artist")
#         self.artist_song_results_frame.grid(row=0, column=0, sticky=tk.E+tk.W+tk.N+tk.S)
#         self.list_ = tk.Listbox(self.artist_song_results_frame, width=45, height=10, listvariable=Results.list_items, selectmode=tk.SINGLE)
#         self.list_.bind("<<ListboxSelect>>", self.handle_results_click)
#         self.list_.grid(row=0, column=0, sticky=tk.E+tk.W+tk.N+tk.S, padx=5, pady=5)
#         self.scrollbar = tk.Scrollbar(self.list_)
#         self.scrollbar.config(command=self.list_.yview)
#         self.list_.config(yscrollcommand=self.scrollbar.set)
#         self.lyrics = Results.lyrics
# 
#         # lyrics results
#         self.lyrics_results_frame = ttk.LabelFrame(self, text="Lyrics")
#         self.lyrics_results_frame.grid(row=1, column=0, sticky=tk.E+tk.W+tk.N+tk.S)
#         self.lyrics = tk.scrolledtext.ScrolledText(self.lyrics_results_frame, height=25, width=60, wrap=tk.WORD)
# #         Results.lyrics = self.lyrics
#         self.lyrics.grid(row=0, column=0, sticky=tk.E+tk.W+tk.N+tk.S, padx=5, pady=5)
#         self.lyrics.tag_configure("highlight", background="yellow", foreground="black")
# 
# 
    def handle_results_click(self, option: str) -> None:
        """Load the selected song's lyrics into the lyrics box."""
        selection = None
        index = self.list_.curselection()
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

    def show_lyrics(self) -> None:
        """Load the lyrics results into the text box."""
        box = self.lyrics
        data = Results.list_items
        if data:
            box.delete("1.0", tk.END)
            box.insert("1.0", data)
        else:
            box.delete("1.0", tk.END)
            box.delete("1.0", tk.END)
            box.insert("1.0", "No matching results.")




