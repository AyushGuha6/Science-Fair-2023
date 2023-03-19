from muse_stream import MuseStream
import time
from matplotlib import pyplot as plt, animation
import subprocess
from animateMuse import Graph
#from eye_blink import DetectEyeBlink
from gsr import GSR_reader
from threading import Thread

def asyncBlink():
    subprocess.run('start /wait python eye_blink.py', shell=True)


eyeT = Thread(target=asyncBlink,
              args=(),
              daemon=True)
eyeT.start()

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
    
    eyeT.join()