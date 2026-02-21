import tkinter as tk
from tkinter import ttk
import threading
import time  # simulering av API-call


# Mock – byt mot din riktiga SchenkerClient
class SchenkerClient:
    def track(self, tracking_number: str):
        time.sleep(2)  # simulera nätverksanrop
        return {
            "tracking_number": tracking_number,
            "status": "In transit",
            "location": "Örebro"
        }


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Schenker Tracking")
        self.geometry("600x300")

        self.client = SchenkerClient()

        self._build_ui()

    # ---------------- UI ----------------

    def _build_ui(self):
        main = ttk.Frame(self, padding=20)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Enter parcel ID").pack(pady=5)

        self.entry = ttk.Entry(main, width=40)
        self.entry.pack(pady=5)

        self.button = ttk.Button(
            main,
            text="Track",
            command=self.start_tracking
        )
        self.button.pack(pady=5)

        self.progress = ttk.Progressbar(
            main,
            mode="indeterminate"
        )

        self.result_label = ttk.Label(main, text="")
        self.result_label.pack(pady=10)

    # ---------------- Logic ----------------

    def start_tracking(self):
        tracking_number = self.entry.get().strip()

        if not tracking_number:
            self.result_label.config(text="Please enter a tracking number")
            return

        # UI state
        self.button.config(state="disabled")
        self.result_label.config(text="")
        self.progress.pack(pady=5)
        self.progress.start()

        # Start background thread
        thread = threading.Thread(
            target=self._track_in_background,
            args=(tracking_number,),
            daemon=True
        )
        thread.start()

    def _track_in_background(self, tracking_number):
        try:
            result = self.client.track(tracking_number)
            self.after(0, self._update_ui_success, result)
        except Exception as e:
            self.after(0, self._update_ui_error, str(e))

    # ---------------- UI Updates ----------------

    def _update_ui_success(self, result):
        self.progress.stop()
        self.progress.pack_forget()
        self.button.config(state="normal")

        text = (
            f"Tracking: {result['tracking_number']}\n"
            f"Status: {result['status']}\n"
            f"Location: {result['location']}"
        )

        self.result_label.config(text=text)

    def _update_ui_error(self, error):
        self.progress.stop()
        self.progress.pack_forget()
        self.button.config(state="normal")

        self.result_label.config(text=f"Error: {error}")


if __name__ == "__main__":
    App().mainloop()