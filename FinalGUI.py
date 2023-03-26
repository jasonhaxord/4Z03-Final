import time
import serial
from scipy.signal import find_peaks
import pyaudio
import wave
import sys
import tkinter as tk
from tkinter import ttk
import threading

# holy mother of imports
bpm = 0
CHUNK = 1024  # idk dont change this
wf = wave.open("sample2.wav", 'rb')  # reads .wav file
p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)  # opens the stream for audio playback
running = False
current_bpm_label = None


# this updates the bpm periodically, every time it is called
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
        time.sleep(
            beat_interval)  # this is super important, this is what makes the program not play the beat over and over at like 100000beats/minute. This makes the program pause for (60/bpm) seconds


# Function to read Arduino data from the USB port, analyze it for peaks, and update with BPM
def analyze_arduino():
    arduino_data = serial.Serial('com3',
                                 115200)  # the way that this is written, it will only work on usb port labelled 'com3'. could be a problem, but we'll see.

    # one thing to note: time is given in seconds since Jan 1, 1970 12:00:00 UTC. Since we're working in seconds and subtracting between times, this doesn't matter.

    last_time = 0

    combined_array = {}

    all_peak_times = []
    counter = 0

    while running:

        current_time = time.time()  # get current time in seconds since ^^^
        # this will only change once per cycle, so we know how much time has passed since the last loop through

        while not arduino_data.inWaiting():  # this will freeze the program if there's a pileup of data from arduino. not a problem.
            pass

        data_packet = float(str(arduino_data.readline(),
                                'utf-8').strip())  # Get, clean and convert reply to a number instead of text (thanks arduino)
        # print(data_packet)
        combined_array[data_packet] = current_time  # stores time at this acceleration value into an array

        def analyseAccelData():

            peak_times = [combined_array[_time_] for _time_ in
                          find_peaks(list(combined_array.keys()), height=95, distance=5)[1][
                              'peak_heights']]  # finds peak times based on analyzing acceleration array, then looking for its corresponding time as a dictionary key. Python OP.

            print(peak_times)  # debugging purposes, useless

            all_peak_times.extend(
                peak_times)  # adds to a big list of times @ peaks, so we know how much time has passed since last peak

        if current_time - last_time > 10:  # set to run this every 10 seconds
            analyseAccelData()
            combined_array.clear()  # clears the acceleration + time array so we don't explode computers after a few minutes of running
            last_time = current_time  # update the current time for the next cycle
            counter += 1  # count 3 of these 10 second cycles, after 3 will average out all the differences between times and give you avg bpm
            if counter >= 3 and len(all_peak_times) >= 2:
                average_difference = sum(
                    [all_peak_times[_tmp_] - all_peak_times[_tmp_ - 1] for _tmp_ in range(1, len(all_peak_times))]) / (
                                             len(
                                                 all_peak_times) - 1)
                all_peak_times.clear()  # cleaning
                print(f'Average BPM: {60 / average_difference}')  # debugging
                update_bpm(60 / average_difference)  # updates bpm for music player and GUI
                counter = 0  # reset counter


# Main loop, everything is called & generated here in an endless loop until program is killed
def main():
    global running, current_bpm_label, bpm
    root = tk.Tk()
    root.geometry('950x300')
    root.title('Gait Rhythm Trainer ver 0.1')
    root.iconbitmap("icon.ico")

        def save_data():
        if not running:
            age = int(age_entry.get())
            gender = str(gender_var.get())

            # Do something with the data
            print(gender)
            print(age)

            if gender == "Female":
                if age < 70:
                    update_bpm(113)
                if age > 70 & age < 75:
                    update_bpm(113)
                if age > 75 & age < 80:
                    update_bpm(114)
                if age > 80 & age < 85:
                    update_bpm(110)
                if age > 85:
                    update_bpm(108)

            else:
                if age < 70:
                    update_bpm(102)
                if age > 70 & age < 75:
                    update_bpm(102)
                if age > 75 & age < 80:
                    update_bpm(106)
                if age > 80 & age < 85:
                    update_bpm(103)
                if age > 85:
                    update_bpm(102)

        # Clear the input fields

        age_entry.delete(0, tk.END)
        gender_var.set('')

    def start_button():
        global running
        if not running:
            running = True
            # do not ask me what the fuck is going on from lines 132-136, i do not know i only know this makes it work gud
            # best guess: this lets the program "multitask", so one thread is checking bpm updates, one thread is playing the audio
            # Start the beat loop in a separate thread
            loop_thread = threading.Thread(target=play_loop)
            loop_thread.start()
            # Start the analysis loop in a separate thread
            analysis_thread = threading.Thread(target=analyze_arduino)
            analysis_thread.start()

    def quit_button():
        global running
        running = False
        root.destroy()

    # Age
    age_label = tk.Label(root, text="Age:", font=("Helvetica", 12))
    age_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
    age_entry = tk.Entry(root, font=("Helvetica", 12))
    age_entry.grid(row=0, column=1, padx=10, pady=10)

    # Gender
    gender_label = tk.Label(root, text="Gender:", font=("Helvetica", 12))
    gender_label.grid(row=0, column=2, sticky='w', padx='50')
    gender_options = ["Male", "Female"]
    gender_var = tk.StringVar(root)
    gender_dropdown = tk.OptionMenu(root, gender_var, *gender_options)
    gender_dropdown.config(width=10, font=("Helvetica", 12))
    gender_dropdown.grid(row=0, column=2, padx='150')

    # Save button
    save_button = tk.Button(root, text="Save Client Info", font=("Helvetica", 12), command=save_data)
    save_button.grid(row=0, column=4, padx=10, pady=10)
    # Add text for current BPM value
    current_bpm_label = tk.Label(root, text=f'Current BPM: {bpm}', font=("Helvetica", 18, "bold"))
    current_bpm_label.grid(row=1, column=2, pady=10)

    # Add an extra column to center the slider
    tk.Label(root, text="", width=2).grid(row=2, column=0)

    # BPM text and Slider
    bpm_slider = ttk.Scale(root, from_=30, to=240, orient='horizontal', length=400,
                           command=lambda val: update_bpm(val))
    bpm_slider.set(bpm)  # set default BPM value
    bpm_slider.grid(row=2, column=2, pady=10)

    # Add text for min and max BPM values
    min_bpm_label = tk.Label(root, text='30', font=("Helvetica", 12))
    min_bpm_label.grid(row=2, column=1, pady=10, sticky='e')

    max_bpm_label = tk.Label(root, text='240', font=("Helvetica", 12))
    max_bpm_label.grid(row=2, column=3, pady=10)

    # Start Button
    start_button = tk.Button(root, text='Start', font=("Helvetica", 12), command=start_button)
    start_button.grid(row=4, column=2)

    # Quit Button
    quit_button = tk.Button(root, text='Quit', font=("Helvetica", 12), command=quit_button)
    quit_button.grid(row=5, column=2, pady='30')

    def update_slider_position():  # updates the position of the slider based on the current BPM value.

        bpm_slider.set(bpm)
        current_bpm_label.config(text=f'Current BPM: {bpm}')
        root.after(100, update_slider_position)

    # Schedule the update_slider_position function to be called every 100 milliseconds
    root.after(100, update_slider_position)

    # Schedule the update_slider_position function to be called every 100 milliseconds
    root.after(100, update_slider_position)

    root.mainloop()  # gui loop, this will run endlessly until program exits


# this makes the program not "crash to exit"
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        running = False
        sys.exit(69)  # yea
