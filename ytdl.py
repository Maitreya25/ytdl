import tkinter as tk
from tkinter import ttk
from yt_dlp import YoutubeDL
from threading import Thread
import time
from tkinter import filedialog
import os
import sys

# Function to get the directory where the script is located
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

ffmpeg_path = resource_path("ffmpeg.exe")

def verify_link():
    link = link_entry.get()
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'noplaylist': True,
            'ffmpeg_location': ffmpeg_path
        }
        with YoutubeDL(ydl_opts) as ydl:
            global info
            info = ydl.extract_info(link, download=False)
            resolutions = sorted(set(f"{f['height']}p" for f in info['formats'] if 'height' in f))
            resolution_combobox.config(values=resolutions)
            resolution_combobox.current(0)
            download_button.config(state=tk.NORMAL)
            status_label.config(text="Link verified.")
    except Exception as e:
        status_label.config(text=str(e))

def download_video(selected_resolution):
    try:
        current_time = str(int(time.time()))
        file_name = f"{info['title']} - {selected_resolution} - {current_time}.mp4"
        default_location = os.path.join(os.path.expanduser('~'), 'Downloads')
        file_path = filedialog.asksaveasfilename(initialfile=file_name, defaultextension=".mp4", initialdir=default_location)
        
        if file_path:
            ydl_opts = {
                'format': f"bestvideo[height={selected_resolution[:-1]}]+bestaudio/best[height={selected_resolution[:-1]}]",
                'outtmpl': file_path,
                'noplaylist': True,
                'ffmpeg_location': ffmpeg_path,
                'progress_hooks': [on_progress]
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([link_entry.get()])
            status_label.config(text="Download completed!")
            progress_bar['value'] = 0
            progress_label.config(text="")
            download_another_button.config(state=tk.NORMAL)
    except Exception as e:
        status_label.config(text=str(e))

def on_progress(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes', 0)
        percentage = (downloaded_bytes / total_bytes) * 100 if total_bytes else 0
        progress_bar['value'] = percentage
        progress_label.config(text=f"{percentage:.2f}% Downloaded")

def download_selected():
    selected_resolution = resolution_combobox.get()
    if selected_resolution:
        status_label.config(text="Downloading...")
        global download_thread
        download_thread = Thread(target=download_video, args=(selected_resolution,))
        download_thread.start()
    else:
        status_label.config(text="Invalid resolution selected.")

def reset_ui():
    link_entry.delete(0, tk.END)
    resolution_combobox.set('')
    progress_bar['value'] = 0
    progress_label.config(text='')
    status_label.config(text='')
    download_button.config(state=tk.DISABLED)
    download_another_button.config(state=tk.DISABLED)


root = tk.Tk()
root.title("YouTube Downloader")

link_label = ttk.Label(root, text="Enter link:")
link_label.grid(row=0, column=0, padx=5, pady=5)

link_entry = ttk.Entry(root, width=40)
link_entry.grid(row=0, column=1, padx=5, pady=5)

verify_button = ttk.Button(root, text="Verify", command=verify_link)
verify_button.grid(row=0, column=2, padx=5, pady=5)

download_button = ttk.Button(root, text="Download", command=download_selected, state=tk.DISABLED) 
download_button.grid(row=0, column=3, padx=5, pady=5)

resolution_label = ttk.Label(root, text="Select resolution:")
resolution_label.grid(row=1, column=0, padx=5, pady=5)

resolution_combobox = ttk.Combobox(root, width=30)
resolution_combobox.grid(row=1, column=1, padx=5, pady=5)

progress_frame = ttk.Frame(root)
progress_frame.grid(row=2, columnspan=4, padx=5, pady=5)

progress_label = ttk.Label(progress_frame, text="")
progress_label.grid(row=0, column=0, padx=5, pady=5)

progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', length=200, mode='determinate')
progress_bar.grid(row=0, column=1, padx=5, pady=5)

status_label = ttk.Label(root, text="")
status_label.grid(row=3, columnspan=4, padx=5, pady=5)

download_another_button = ttk.Button(root, text="Download Another", command=reset_ui, state=tk.DISABLED)
download_another_button.grid(row=4, column=1, columnspan=2, padx=5, pady=5)

copyright_label = ttk.Label(root, text="Copyright © 2024 Maitreya Patni", foreground="gray")
copyright_label.grid(row=4, column=0, columnspan=2, sticky="sw", padx=5, pady=(0, 5))


root.mainloop()
