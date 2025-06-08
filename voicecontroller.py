import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import sounddevice as sd
import soundfile as sf
import numpy as np
import os
import threading
import uuid

AUDIO_DIR = "audio_logs"
os.makedirs(AUDIO_DIR, exist_ok=True)

sample_rate = 44100
channels = 1
duration = 5  # default record time

logs = []  # stores metadata

# ========== Voice Effects ==========
def apply_effect(audio_data, effect):
    if effect == "Normal":
        return audio_data
    elif effect == "Chipmunk":
        return audio_data[::2]  # basic pitch-up
    elif effect == "Deep":
        stretched = np.interp(np.linspace(0, len(audio_data), len(audio_data)*2),
                              np.arange(len(audio_data)), audio_data)
        return stretched
    elif effect == "Robot":
        mod = np.sin(2 * np.pi * np.arange(len(audio_data)) * 20 / sample_rate)
        return audio_data * mod
    return audio_data

# ========== Recording =============
def record_audio(name, label, effect):
    record_button.config(state=tk.DISABLED)
    status_label.config(text="Recording...")
    data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels)
    sd.wait()
    status_label.config(text="Recording Done.")
    
    modified = apply_effect(data.flatten(), effect)
    filename = f"{AUDIO_DIR}/{uuid.uuid4().hex[:8]}_{name}.wav"
    sf.write(filename, modified, sample_rate)
    logs.append((name, label, filename))
    refresh_log_list()
    record_button.config(state=tk.NORMAL)

def start_recording():
    name = simpledialog.askstring("Recording Name", "Enter a name for this recording:")
    if not name:
        return
    label = simpledialog.askstring("Label", "Enter a label (e.g., idea, reminder):")
    effect = voice_effect_var.get()
    threading.Thread(target=record_audio, args=(name, label, effect)).start()

# ========== Playback ==========
def play_selected():
    selected = log_listbox.curselection()
    if not selected:
        messagebox.showinfo("Info", "Select a recording to play.")
        return
    _, _, path = logs[selected[0]]
    data, sr = sf.read(path)
    sd.play(data, sr)
    sd.wait()

# ========== GUI ==========
root = tk.Tk()
root.title("🎙️ Voice Logger")

frame = ttk.Frame(root, padding=10)
frame.pack(fill='both', expand=True)

record_button = ttk.Button(frame, text="🔴 Record New Audio", command=start_recording)
record_button.grid(row=0, column=0, pady=5, sticky='ew')

ttk.Button(frame, text="▶️ Play Selected", command=play_selected).grid(row=0, column=1, padx=5, pady=5, sticky='ew')

voice_effect_var = tk.StringVar(value="Normal")
ttk.Label(frame, text="Effect:").grid(row=1, column=0, sticky='w')
ttk.OptionMenu(frame, voice_effect_var, "Normal", "Normal", "Chipmunk", "Deep", "Robot").grid(row=1, column=1, sticky='ew')

log_listbox = tk.Listbox(frame, width=60)
log_listbox.grid(row=2, column=0, columnspan=2, pady=10)

status_label = ttk.Label(frame, text="Ready.", anchor='center')
status_label.grid(row=3, column=0, columnspan=2)

def refresh_log_list():
    log_listbox.delete(0, tk.END)
    for i, (name, label, path) in enumerate(logs):
        log_listbox.insert(tk.END, f"{i+1}. {name} [{label}]")

refresh_log_list()
root.mainloop()
