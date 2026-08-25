import heartpy as hp
import matplotlib.pyplot as plt
import csv
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# load example data
with open(DATA_DIR / "ppg_raw.csv") as raw_data:
    data = (np.transpose(np.array((list(csv.reader(raw_data, delimiter='\t')))))[
            1][0:1100]).astype(float)
    print(data)
    print(type(data))
    print(len(data))
    '''# this example set is sampled at 100Hz
    data, _ = hp.load_exampledata(1)[-40:]
    print("EEE", data)
    print(type(data))
    print(len(data))'''
    # data = hp.filtering.filter_signal(  data, cutoff=5, sample_rate=64.0, order=3, filtertype='lowpass')
    # data = hp.filtering.hampel_correcter(data, 64)
    # data = hp.enhance_peaks(data)
    data = hp.filtering.smooth_signal(data, sample_rate=64.0, window_length=6)
    data = hp.filtering.filter_signal(hp.filtering.hampel_correcter(np.around(
        data), 64), [0.7, 3.5], sample_rate=64.0, order=2, filtertype="bandpass")
    plt.figure(figsize=(12, 4))
    plt.plot(data)
    plt.show()
    working_data, measures = hp.process(
        data, 64.0, report_time=True)  # , clean_rr = True)
    # working_data, measures = hp.process(data, sample_rate=64.0, calc_freq=True, interp_clipping=True,
    #                                    clipping_scale=True, reject_segmentwise=True, clean_rr=True, report_time=True)
    img = hp.plotter(working_data, measures, show=False)
    print(measures.keys())
    print(measures['rmssd'])
    plt.show()
    # print(measures.keys())
    # print(measures['bpm'])  # returns BPM value
    # print(measures['rmssd'])  # returns RMSSD HRV measure (lower = higher stress)
    # sd1 is short term variability
    # sd2 is long term variability

    # High-frequency power is highly correlated with the pNN50 and RMSSD time-domain measures (10). HF band power may increase at night and decrease during the day (1). Lower HF power is correlated with stress, panic, anxiety, or worry.

    # 40 SECONDS
    # process_segmentwise
    # working_data, measures = hp.process_segmentwise(data, sample_rate=100.0, segment_width = 40, segment_overlap = 0.25)

# 'bpm', 'ibi', 'sdnn', 'sdsd', 'rmssd', 'pnn20', 'pnn50', 'hr_mad', 'sd1', 'sd2', 's', 'sd1/sd2', 'breathingrate'])grate'


# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5624990/#:~:text=It%20is%20calculated%20by%20first,average%20of%20these%20288%20values.
# increases in stress were associated with decreases in the RR interval
