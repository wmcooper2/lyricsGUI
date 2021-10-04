import time
import threading
import tkinter as tk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.button = tk.Button(self, command=self.start_action, text="Wait 2 seconds")
        self.button.pack(padx=20, pady=20)

    def start_action(self):
        self.button.config(state=tk.DISABLED)

        #THREADING
        thread = threading.Thread(target=self.run_action)
        print(threading.main_thread().name)
        print(thread.name)
        thread.start()
        self.check_thread(thread)

    def check_thread(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.check_thread(thread))
        else:
            self.button.config(state=tk.NORMAL)

    def run_action(self):
        print("Starting long running action.")
        time.sleep(3)
        print("Ended long action.")

#         self.after(2000, lambda: self.button.config(state=tk.NORMAL))
     
if __name__ == "__main__":
    app = App()
    app.mainloop()

