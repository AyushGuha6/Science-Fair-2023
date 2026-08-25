import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#import gsr
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions, DetrendOperations
import csv
import datetime
import os
import mne
from mne.channels import read_layout
from pathlib import Path
path = str(Path(__file__).resolve().parents[2] / "data")
if not os.path.exists(path):
    os.mkdir(path)
from threading import Thread

fileTime = str(datetime.date.today()) + "-"+ str(datetime.datetime.now().strftime("%H.%M.%S"))
def get_values(d):
    t = time.time()
    DataFilter.detrend(d[eeg_channel], DetrendOperations.LINEAR.value)

    psd = DataFilter.get_psd_welch(d[eeg_channel], nfft, nfft // 2, sampling_rate, WindowFunctions.HANNING.value)
    #print("psd",psd)
    #plt.plot(psd[1][:60], psd[0][:60])
    #plt.show()

    # calc band power
    delta = DataFilter.get_band_power(psd, 0, 4.0)
    theta = DataFilter.get_band_power(psd, 4, 8.0)
    alpha = DataFilter.get_band_power(psd, 8.0, 12.0)
    beta = DataFilter.get_band_power(psd, 12.0, 30.0)
    gamma = DataFilter.get_band_power(psd, 30.0, 50.0)
    return [t, delta, theta, alpha, beta, gamma, 
            #gsr.getGSR, 
            d[11], d[12], d[13]]
params = BrainFlowInputParams()
#params.mac_address = "00:55:da:b7:c2:2f"
board_id=38
board = BoardShim(board_id, params)
sampling_rate = BoardShim.get_sampling_rate(board_id)
nfft = DataFilter.get_nearest_power_of_two(sampling_rate)
eeg_channels = BoardShim.get_eeg_channels(board_id)
eeg_channel = eeg_channels[0]
def main():

    board.prepare_session()
    board.start_stream()
    with open(path + "/raw_data_"+ fileTime+".csv", "a", newline='') as csv_file:
        try:
            writer = csv.writer(csv_file)
            print(BoardShim.get_board_descr(board_id))
            print(BoardShim.get_ppg_channels(board_id))
            while True:
                time.sleep(5)
                data = board.get_board_data()

                writer.writerow(get_values(data))
                #for i in data[11]:
                #    print(i)

        except KeyboardInterrupt:
            print("close")
        finally:
            board.stop_stream()
            board.release_session()





#eeg_data = eeg_data / 1000000 # BrainFlow returns uV, convert to V for MNE

#ch_types = ['eeg'] * len(eeg_channels)
#ch_names = BoardShim.get_eeg_names(41)
#print(ch_names)
#sfreq = BoardShim.get_sampling_rate(41)
#info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
#raw = mne.io.RawArray(eeg_data, info)
# its time to plot something!
#raw.plot_psd(average=False)


if __name__ == "__main__":
    t = Thread(target=main)
    t.daemon = True

    t.start()
    
    states = ("relaxed", "semi-stressed", "stressed")
    timestamps = []
    time.sleep(2)
    with open(path + "/timestamps_"+ fileTime+".txt", "w", newline='') as timeFile:
        try:
            while True:
                input("press enter to go to next stage\n")
                timestamps.append(time.time())
        except KeyboardInterrupt:
            print('Closing!')
        finally:
            print(timestamps)
            timeFile.write(str(dict(zip(states,timestamps))))       