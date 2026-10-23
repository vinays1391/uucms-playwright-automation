import argparse
import ctypes
import os
import queue
import subprocess
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

from dotenv import load_dotenv


load_dotenv()
ROOT_DIR = Path(__file__).resolve().parent.parent
VENV_PYTHON = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
RECORDINGS_DIR = ROOT_DIR / "recordings"

user32 = ctypes.windll.user32
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
user32.EnumWindows.argtypes = [EnumWindowsProc, ctypes.c_void_p]
user32.GetWindowTextW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]
user32.IsWindowVisible.argtypes = [ctypes.c_void_p]
user32.PostMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p]


def find_codegen_windows(exclude_hwnds):
    found = []

    def callback(hwnd, _):
        if hwnd in exclude_hwnds:
            return True
        buffer = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buffer, 512)
        title = buffer.value
        if title and user32.IsWindowVisible(hwnd) and "codegen" in title.lower():
            found.append((hwnd, title))
        return True

    user32.EnumWindows(callback, None)
    return found


def close_codegen_windows(exclude_hwnds):
    windows = find_codegen_windows(exclude_hwnds)
    for hwnd, _ in windows:
        user32.PostMessageW(hwnd, 0x0010, None, None)
    return windows


class RecorderPanel:
    def __init__(self, root, url, browser, output_path):
        self.root = root
        self.url = url
        self.browser = browser
        self.output_path = output_path
        self.proc = None
        self.events = queue.Queue()
        self.own_hwnds = set()

        root.title("UUCMS Codegen Recorder")
        root.geometry("520x210")
        root.protocol("WM_DELETE_WINDOW", self.on_close)

        frame = tk.Frame(root, padx=14, pady=12)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text=f"Target: {url}", anchor="w", wraplength=480).grid(
            row=0, column=0, sticky="w"
        )
        tk.Label(frame, text=f"Output: {output_path}", anchor="w", wraplength=480).grid(
            row=1, column=0, sticky="w", pady=(6, 0)
        )
        self.button = tk.Button(frame, text="Start Codegen", command=self.on_toggle)
        self.button.grid(row=2, column=0, sticky="w", pady=(12, 0))
        self.status = tk.Label(frame, text="Ready.", anchor="w", wraplength=480)
        self.status.grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.poll_events()

    def own_window_hwnds(self):
        client = int(self.root.winfo_id())
        parent = user32.GetParent(client)
        return {hwnd for hwnd in (client, parent) if hwnd}

    def poll_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                if event[0] == "done":
                    _, returncode, size = event
                    self.proc = None
                    self.button.config(text="Start Codegen", state="normal")
                    self.status.config(foreground="black")
                    if returncode == 0 and size:
                        self.status.config(text=f"Saved: {self.output_path.name} ({size // 1024} KB)")
                    else:
                        self.status.config(text=f"Codegen exited (code {returncode}). Check the console.")
        except queue.Empty:
            pass
        self.root.after(150, self.poll_events)

    def on_toggle(self):
        if self.proc is None:
            self.start()
        else:
            self.stop()

    def start(self):
        self.own_hwnds = self.own_window_hwnds()
        RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
        cmd = [
            str(VENV_PYTHON),
            "-m",
            "playwright",
            "codegen",
            f"--browser={self.browser}",
            "--target=python",
            f"--output={self.output_path}",
            self.url,
        ]
        self.proc = subprocess.Popen(cmd, cwd=str(ROOT_DIR))
        self.button.config(text="Stop Codegen")
        self.status.config(text="Recording... do the workflow in the codegen browser window.", foreground="red")
        print(f"[record-codegen] starting: {' '.join(cmd)}")
        print("[record-codegen] live generated code appears in this console.")
        threading.Thread(target=self.monitor, daemon=True).start()

    def stop(self):
        if self.proc.poll() is not None:
            self.status.config(text="Codegen already finished; report incoming...")
            return
        windows = close_codegen_windows(self.own_hwnds)
        if windows:
            self.status.config(text="Closing codegen browser; saving file...")
        else:
            self.status.config(text="Could not find the codegen window. Close it manually to save.")
            print("[record-codegen] could not find the codegen browser window; close it manually to save the file.")

    def monitor(self):
        returncode = self.proc.wait()
        size = self.output_path.stat().st_size if self.output_path.exists() else 0
        if returncode == 0 and size:
            print(f"[record-codegen] saved: {self.output_path} ({size // 1024} KB)")
            print("[record-codegen] next: feed this file to prompts/<module>-pom-conversion.md to write the POM and tests.")
        else:
            print(f"[record-codegen] codegen exited with code {returncode}; the file may not have been saved.")
        self.events.put(("done", returncode, size))

    def on_close(self):
        if self.proc is not None and self.proc.poll() is None:
            if not messagebox.askyesno(
                "UUCMS Codegen Recorder", "Codegen is still running.\nClose it and save the file?"
            ):
                return
            close_codegen_windows(self.own_hwnds)
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description="Button panel for Playwright codegen recording.")
    parser.add_argument("--url", default=os.getenv("UUCMS_BASE_URL", "http://123.63.4.210:5010/"))
    args = parser.parse_args()
    browser = os.getenv("UUCMS_BROWSER", "chromium").strip().lower()
    if browser not in ("chromium", "firefox", "webkit"):
        raise ValueError("UUCMS_BROWSER must be chromium, firefox, or webkit")
    if not VENV_PYTHON.exists():
        raise FileNotFoundError(f"venv python not found at {VENV_PYTHON}")
    output_path = RECORDINGS_DIR / f"workflow_{datetime.now():%Y%m%d_%H%M%S}_codegen.py"
    root = tk.Tk()
    RecorderPanel(root, args.url, browser, output_path)
    root.mainloop()


if __name__ == "__main__":
    main()
