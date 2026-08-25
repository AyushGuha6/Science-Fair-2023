import os
os.environ["BLINKA_MCP2221"] = "1"
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from analogio import AnalogIn
import hid
import time
import board
from queue import Queue
from threading import Thread
import utils
import datetime

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
# os.environ["BLINKA_MCP2221"] = "1" must be ran before all others
# do not pip install hid

class GSR_reader():
    def __init__(self):
        self.device = hid.device()
        self.device.open(0x04D8, 0x00DD)

        self.gsr = AnalogIn(board.G1)
        self.filename = "gsr.csv"
        


    def get_voltage(self, raw, operating=5.0):
        return raw * operating / 65536

    def get_serial(self, volts, operating=5.0, maxSerial=512):
        return volts * maxSerial/operating

    def get_serial_raw(self, raw, operating=5.0, maxSerial=512):
        return (raw * 5.0 / 65536) * maxSerial/operating

    def mainloop(self, queue, operatingVoltage=5.0, maxSerial=512, sleep = 0.2):
        while True:
            raw = self.gsr.value
            volts = self.get_voltage(raw)
            serial = self.get_serial(volts, operatingVoltage)
            queue.put("{:s}{:d},{:.2f},{:.0f},{:.0f}\n".format(str(datetime.datetime.now()), raw, volts, serial, ((1024+2*serial)*10000)/(maxSerial-serial)))
            time.sleep(sleep)
            
    def start(self, fileName="gsr", operatingVoltage=5.0, maxSerial=512, sleep=0.2, debug=False):
        self.filename = str(DATA_DIR / f"{fileName}_{datetime.date.today()}-{datetime.datetime.now().strftime('%H.%M.%S')}.csv")

        loggerQueue = Queue(maxsize=1024)
        writerThread = Thread(target=utils.file_writer, args=(self.filename, loggerQueue, debug), daemon=True)
        writerThread.start()
        
        dataThread = Thread( target=self.mainloop, args=(
            loggerQueue, operatingVoltage, maxSerial, sleep), daemon=True)
        dataThread.start()
        #time.sleep(100)
    

if __name__ == "__main__":
    '''print(dir(board))
    # all usb devices
    # hid.enumerate()
    # volts = get_voltage(raw)
    # serial = get_serial(volts, 5.0)
    # print(os.environ["BLINKA_MCP2221"])

    while True:
        raw = gsr.value
        volts = get_voltage(raw)
        serial = get_serial(volts, 5.0)
        print("raw = {:5d},    volts = {:5.2f},    serial = {:5.0f}      human_res = {:5.0f}".format(
            raw, volts, serial, ((1024+2*serial)*10000)/(512-serial)))
        time.sleep(0.05)'''
    g = GSR_reader().start("test")
