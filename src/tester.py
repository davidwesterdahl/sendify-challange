import json
from schenkers_api import SchenkerClient
from configparser import ConfigParser
from tkinter import ttk
import tkinter as tk
import threading

config = ConfigParser()
if not config.read("settings.cfg"):
    print("File not found")
URL = config.get("WEBBSITE", "url")
REF_ID = config.get("WEBBSITE", "debug_id")

client = SchenkerClient()

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Schenker Test")
        self.root.geometry("800x400")
        self.main = ttk.Frame(self.root, padding=5)
        self.main.pack(fill="both", expand=True)

        self.warning_label = ttk.Label(self.main, text=" ")
        self.warning_label.pack()
        self.label = ttk.Label(self.main, text="Enter the parcel ID")
        self.label.pack()

        self.entry = tk.Entry(self.main)
        self.entry.pack()
        self.button = ttk.Button(self.main, text="Enter", command=self.button_press)
        self.button.pack()

        self.answer = ttk.Label(self.main)
        self.answer.pack(fill="both", expand=True)
        self.answer_scroll = ttk.Scrollbar(self.answer)
        self.answer_scroll.pack(anchor="e", side="right")


        self.root.mainloop()

    def button_press(self):
        self.answer.configure(text="Loading...")
        entry = self.entry.get()
        response = (json.dumps(client.parse_json(client.fetch_json(URL, entry)), sort_keys=True, indent=4))
        self.answer.configure(text=response)


app = App()
#print(json.dumps(client.parse_json(client.fetch_json(URL, REF_ID)), sort_keys=True, indent=4))