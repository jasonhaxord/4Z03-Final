import time
import serial
import threading
from scipy.signal import find_peaks
import pyaudio
import wave
import sys
import tkinter as tk

CHUNK = 1024
bpm = 60
beat_interval = 60 / bpm
wf = wave.open("sample2.wav", 'rb')
p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
running= False
current_bpm_label = None
def update_bpm(val):
    global bpm, beat_interval
    bpm = int(round(float(val)))
    beat_interval = 60 / bpm
    current_bpm_label.config(text=f'Current BPM: {bpm}')


# Function to play one beat
def play_beat():
    wf.rewind()
    data = wf.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)

# Function to play the beats continuously
def play_loop():
    global beat_interval
    while running:
        play_beat()
        beat_interval = 60 / bpm
        time.sleep(beat_interval)

def analyze_arduino():
    arduino_data = serial.Serial('com3', 115200)

    start_time = time.time()

    last_time = 0

    combined_array = {}

    all_peak_times = []
    counter = 0

    while running:

        current_time = time.time()

        while not arduino_data.inWaiting():
            pass

        data_packet = float(str(arduino_data.readline(), 'utf-8').strip())  # Get and clean reply
        # print(data_packet)
        combined_array[data_packet] = current_time

        def analyseAccelData():

            peak_times = [combined_array[_time_] for _time_ in
                          find_peaks(list(combined_array.keys()), height=95, distance=5)[1]['peak_heights']]

            print(peak_times)

            all_peak_times.extend(peak_times)

        if current_time - last_time > 10:
            analyseAccelData()
            combined_array.clear()
            last_time = current_time
            counter += 1
            if counter >= 3 and len(all_peak_times) >= 2:
                average_difference = sum(
                    [all_peak_times[_tmp_] - all_peak_times[_tmp_ - 1] for _tmp_ in range(1, len(all_peak_times))]) / (
                                             len(
                                                 all_peak_times) - 1)
                all_peak_times.clear()
                print(f'Average BPM: {60 / average_difference}')
                update_bpm(60 / average_difference)
                counter = 0


import tkinter as tk
from tkinter import ttk
import threading

def main():
    global running, current_bpm_label, bpm
    root = tk.Tk()
    root.geometry('420x200')
    root.title('Gait Rhythm Trainer ver 0.1')
    root.iconbitmap("icon.ico")

    # Add label for current BPM value
    current_bpm_label = tk.Label(root, text=f'Current BPM: {bpm}')
    current_bpm_label.grid(column=1, row=0, padx=10, pady=10)

    # # BPM Label and Slider
    # bpm_label = tk.Label(root, text='BPM:')
    # bpm_label.grid(column=0, row=1, padx=10, pady=10)

    bpm_slider = ttk.Scale(root, from_=30, to=240, orient='horizontal', length=200,
                           command=lambda val: update_bpm(val))
    bpm_slider.set(bpm)  # set default BPM value
    bpm_slider.grid(row=1, column=1, padx=60)

    # # Add label for current BPM value
    # current_bpm_label = tk.Label(root, text=f'Current BPM: {bpm}')
    # current_bpm_label.grid(row=1, column=0, columnspan=2)

    # Add label for min and max BPM values
    min_bpm_label = tk.Label(root, text='30')
    min_bpm_label.grid(row=1, column=0, sticky = 'W', padx=10)

    max_bpm_label = tk.Label(root, text='240')
    max_bpm_label.grid(row=1, column=3,sticky = 'E')

    # Start Button
    def start_button():
        global running
        if not running:

            running = True
            # Start the beat loop in a separate thread
            loop_thread = threading.Thread(target=play_loop)
            loop_thread.start()
            # Start the analysis loop in a separate thread
            analysis_thread = threading.Thread(target=analyze_arduino)
            analysis_thread.start()

    start_button = tk.Button(root, text='Start', command=start_button)
    start_button.grid(row=12, column=0, padx=10,pady='50')

    # Quit Button
    def quit_button():
        global running
        running = False
        root.destroy()

    quit_button = tk.Button(root, text='Quit', command=quit_button)
    quit_button.grid(row=12, column=3,sticky='S',pady='50')

    def update_slider_position():
        """Updates the position of the slider based on the current BPM value."""
        bpm_slider.set(bpm)
        current_bpm_label.config(text=f'Current BPM: {bpm}')
        root.after(100, update_slider_position)

    # Schedule the update_slider_position function to be called every 100 milliseconds
    root.after(100, update_slider_position)

    # Schedule the update_slider_position function to be called every 100 milliseconds
    root.after(100, update_slider_position)

    root.mainloop()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        running = False
        sys.exit(69)

