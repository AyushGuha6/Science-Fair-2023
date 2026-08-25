from sensors.muse_stream import MuseStream
import time
from matplotlib import pyplot as plt, animation
import numpy as np
from viz.animateMuse import Graph
from vision.eye_blink import DetectEyeBlink
from sensors.gsr import GSR_reader

muse_stream = MuseStream()
conn = muse_stream.connDevice()
#eyeblink = DetectEyeBlink()
#eyeblink.start()
gsr = GSR_reader()
gsr.start("gsr")
time.sleep(6)
if conn:
    muse_stream.startStream()
    muse_stream.start()
    time.sleep(10)
    try:
        g1 = Graph()
        anim = animation.FuncAnimation(g1.fig, g1.animate, interval=10000, fargs=(muse_stream.eeg_file_name,muse_stream.ppg_raw_file_name,gsr.filename), cache_frame_data=False) 
        plt.show()
        plt.close()
    except KeyboardInterrupt:
        print("Closing Program")
    muse_stream.stop()
    muse_stream.stopStream()
    conn = muse_stream.disconnectDevice()