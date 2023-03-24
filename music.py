import tkinter as tk
import pyaudio
import wave
import time
# Set up audio
CHUNK = 1024
wf = wave.open("sample2.wav", 'rb')
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

# Set up initial BPM
bpm = 60
beat_interval = 60 / bpm

# Create the GUI window
window = tk.Tk()
window.title("Beat Player")

# Create a label for the BPM setting
bpm_label = tk.Label(window, text=f"BPM: {bpm}")
bpm_label.pack()

# Create a scale widget for adjusting the BPM
bpm_scale = tk.Scale(window, from_=30, to=240, orient=tk.HORIZONTAL, length=300, command=lambda x: update_bpm(int(x)))
bpm_scale.set(bpm)
bpm_scale.pack()

# Function to update the BPM and beat interval
def update_bpm(new_bpm):
    global bpm, beat_interval
    bpm = int(new_bpm)
    beat_interval = 60 / bpm
    bpm_label.config(text=f"BPM: {bpm}")

# Function to play one beat
def play_beat():
    wf.rewind()
    data = wf.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)

# Function to play the beats continuously
def play_loop():
    while True:
        play_beat()
        time.sleep(beat_interval)

# Start the beat loop in a separate thread
import threading
loop_thread = threading.Thread(target=play_loop)
loop_thread.start()

# Start the GUI event loop
window.mainloop()

# Clean up
wf.rewind()
stream.stop_stream()
stream.close()
p.terminate()

