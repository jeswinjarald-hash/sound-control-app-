import sounddevice as sd
import numpy as np
import time
import threading
import tkinter as tk
from tkinter import ttk
from ctypes import cast, POINTER
from collections import deque
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# =========================
# AUDIO CONSTANTS
# =========================
SAMPLE_RATE = 44100
DURATION = 0.5

RMS_SCALE = 15.0
WINDOW_SIZE = 5
MAX_CHANGE = 0.05

MAX_VOLUME = 0.80
DEADZONE_RMS = 0.003
REACTION_DELAY = 1.2

# =========================
# SYSTEM VOLUME
# =========================
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_,
    CLSCTX_ALL,
    None
)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# =========================
# SHARED STATE
# =========================
running = False
rms_history = deque(maxlen=WINDOW_SIZE)

current_volume = volume.GetMasterVolumeLevelScalar()
latest_input_db = -100.0
latest_output_db = -100.0

# =========================
# AUDIO FUNCTIONS
# =========================
def get_ambient_rms():
    audio = sd.rec(
        int(SAMPLE_RATE * DURATION),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()
    return float(np.sqrt(np.mean(audio ** 2)))

def rms_to_db(rms):
    if rms < 1e-6:
        return -100.0
    return 20 * np.log10(rms)

def volume_to_db(vol):
    if vol <= 0:
        return -100.0
    return 20 * np.log10(vol)

def set_volume_immediate(val):
    """Force system volume immediately"""
    global current_volume
    val = max(min_volume_var.get(), min(MAX_VOLUME, val))
    volume.SetMasterVolumeLevelScalar(val, None)
    current_volume = val

# =========================
# CONTROL LOOP
# =========================
def control_loop():
    global running, current_volume
    global latest_input_db, latest_output_db

    last_rms = 0.0

    while running:
        rms = get_ambient_rms()
        rms_history.append(rms)
        avg_rms = sum(rms_history) / len(rms_history)

        if abs(avg_rms - last_rms) < DEADZONE_RMS:
            time.sleep(REACTION_DELAY)
            continue
        last_rms = avg_rms

        latest_input_db = rms_to_db(avg_rms)

        base_volume = min(avg_rms * RMS_SCALE, 1.0)
        adaptive_volume = base_volume * compensation_var.get()

        # 🔒 Apply minimum immediately
        target_volume = max(min_volume_var.get(), adaptive_volume)
        target_volume = min(MAX_VOLUME, target_volume)

        diff = target_volume - current_volume
        if abs(diff) > MAX_CHANGE:
            target_volume = current_volume + MAX_CHANGE * np.sign(diff)

        set_volume_immediate(target_volume)
        latest_output_db = volume_to_db(current_volume)

        time.sleep(1)

# =========================
# GUI UPDATE LOOP
# =========================
def update_gui():
    input_db_var.set(f"{latest_input_db:.2f} dB")
    output_db_var.set(f"{latest_output_db:.2f} dB")
    volume_var.set(f"{current_volume:.2f}")
    root.after(300, update_gui)

# =========================
# SLIDER CALLBACKS (KEY FIX)
# =========================
def on_min_volume_change(val):
    """Immediately apply new minimum volume"""
    set_volume_immediate(float(val))

def on_compensation_change(val):
    """No immediate volume jump, just update logic"""
    pass

# =========================
# GUI CONTROLS
# =========================
def start():
    global running
    if not running:
        running = True
        threading.Thread(target=control_loop, daemon=True).start()
        status_var.set("Running")

def stop():
    global running
    running = False
    status_var.set("Stopped")

# =========================
# GUI SETUP
# =========================
root = tk.Tk()
root.title("Adaptive Volume Controller (Fixed)")
root.geometry("460x440")
root.resizable(False, False)

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

ttk.Label(frame, text="Adaptive Volume Controller",
          font=("Segoe UI", 16, "bold")).pack(pady=10)

input_db_var = tk.StringVar(value="-- dB")
output_db_var = tk.StringVar(value="-- dB")
volume_var = tk.StringVar(value="0.00")
status_var = tk.StringVar(value="Stopped")

min_volume_var = tk.DoubleVar(value=0.25)
compensation_var = tk.DoubleVar(value=1.2)

ttk.Label(frame, text="Input (Ambient) Volume").pack()
ttk.Label(frame, textvariable=input_db_var,
          font=("Segoe UI", 12)).pack(pady=3)

ttk.Label(frame, text="Output (System) Volume").pack()
ttk.Label(frame, textvariable=output_db_var,
          font=("Segoe UI", 12)).pack(pady=3)

ttk.Label(frame, text="Current System Volume").pack()
ttk.Label(frame, textvariable=volume_var,
          font=("Segoe UI", 12)).pack(pady=3)

# 🔒 MIN VOLUME SLIDER (NOW REALLY WORKS)
ttk.Label(frame, text="Minimum Volume (Locked Floor)").pack(pady=6)
ttk.Scale(
    frame,
    from_=0.05,
    to=0.6,
    variable=min_volume_var,
    command=on_min_volume_change
).pack(fill="x")

# 🔊 COMPENSATION SLIDER
ttk.Label(frame, text="Loudness Compensation").pack(pady=6)
ttk.Scale(
    frame,
    from_=1.0,
    to=1.6,
    variable=compensation_var,
    command=on_compensation_change
).pack(fill="x")

btns = ttk.Frame(frame)
btns.pack(pady=15)

ttk.Button(btns, text="Start", command=start).pack(side="left", padx=10)
ttk.Button(btns, text="Stop", command=stop).pack(side="left", padx=10)

ttk.Label(frame, textvariable=status_var,
          foreground="green").pack(pady=5)

root.after(300, update_gui)
root.mainloop()
