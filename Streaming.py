import time
import numpy as np
import serial

from scipy.signal import find_peaks

arduinoData = serial.Serial('com3', 115200) 

start_time = time.time()
programRunTime = time.time() - start_time

last_time = 0

combined_array = {}
all_peak_times = []

counter = 0

while True:

    programRunTime = int(time.time() - start_time)
   # print(f"runtime {programRunTime} seconds")
    currentTime = time.time()

    while not arduinoData.inWaiting():
        pass

    dataPacket = float(str(arduinoData.readline(), 'utf-8').strip())  # Get and clean reply

    combined_array[dataPacket] = currentTime


    def analyseAccelData():
        # AccelArray = list(combined_array.keys())

        peak_times = [combined_array[_time_] for _time_ in
                      find_peaks(list(combined_array.keys()), height=1, prominence=.5,distance=2)[1]['peak_heights']]
        print(peak_times)
        all_peak_times.extend(peak_times)
        # peaks = find_peaks(AccelArray, height=0, prominence=0)
        # heights = peaks[1]['peak_heights']  # list of the heights of the peaks
        # for height in heights:
        #     print(height)
        #     peak_time = combined_array[height]
        #     print(f'Peak height: {peak_pos} at: {peak_time}')


    if currentTime - last_time > 3:
        analyseAccelData()
        # AccelArray.clear()
        # timeArray.clear()
        combined_array.clear()
        last_time = currentTime
        counter +=1
        if counter >= 5 and len(all_peak_times) >= 2:
            average_difference = sum(
                [all_peak_times[_tmp_] - all_peak_times[_tmp_ - 1] for _tmp_ in range(1, len(all_peak_times))]) / (len(
                all_peak_times) - 1)
            print([(all_peak_times[_tmp_] - all_peak_times[_tmp_ - 1]) for _tmp_ in range(1, len(all_peak_times))])
            all_peak_times.clear()
            print(f'Average BPM: {60/average_difference}')

            counter = 0

    # print(AccelArray)
