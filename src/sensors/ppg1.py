import sys
import datetime
import time
from pathlib import Path
# Multithreading for writing to CSV
from threading import Thread
from queue import Queue
# import the Queue class from Python 3
'''if sys.version_info >= (3, 0):
    from queue import Queue
# otherwise, import the Queue class for Python 2.7
else:
    from Queue import Queue'''

import numpy as np
import pandas as pd

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets
from brainflow.data_filter import DataFilter
from pprint import pprint

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class PpgStream:
    def __init__(self):
        # self.stream_id = stream_id   # default is 0 for primary camera
        self.params = BrainFlowInputParams()
        self.board = BoardShim(BoardIds.MUSE_2_BOARD, self.params)
        self.board_id = BoardIds.MUSE_2_BOARD.value
        pprint(BoardShim.get_board_descr(self.board_id))
        self.ppg_board_desc = BoardShim.get_board_descr(
            self.board_id, preset=BrainFlowPresets.ANCILLARY_PRESET)
        self.ppg_sample_rate = BoardShim.get_sampling_rate(
            self.board_id, BrainFlowPresets.ANCILLARY_PRESET)

        self.stopped = True
        self.conn = False

        print(f"Initiating Thread...")
        self.t = Thread(target=self.startStream, args=(), daemon=True)

    # method for starting the thread
    def start(self):
        self.stopped = False
        self.t.start()
        return self

    def stop(self):
        self.stopped = True
        self.t.join()

    # method for starting the thread for grabbing next available frame in input stream
    def connect(self):
        if self.conn == False:
            print(f'{datetime.datetime.now()} Preparing to connect to the Board...')
            try:
                self.board.prepare_session()
                self.board.config_board('p50')
                print(f'{datetime.datetime.now()} Connected to the Board...')
                self.conn = True
            except Exception as err:
                print(f"{datetime.datetime.now()} Error: {err}")
                # print(f"Unexpected {err=}, {type(err)=}")
                self.conn = False
                # raise

        return self.conn

    def startStream(self):
        while True:
            if self.stopped is True:
                # release all resources
                break
            conn = self.connect()
            print(f"Device Connected: {conn:}")

            if conn:
                self.board.start_stream()
                stream_counter = 40
                print(
                    f'{datetime.datetime.now()} Start streaming for {stream_counter} secs...')
                # time.sleep(200)
                cnt = 0
                while cnt < stream_counter:
                    time.sleep(1)
                    cnt += 1
                    print(
                        f'{datetime.datetime.now()} Streaming Data from Device: {cnt} secs')
                    # print(f'{datetime.datetime.now()} Fetching Data from the Buffer...')
                    data = self.board.get_board_data(
                        preset=BrainFlowPresets.ANCILLARY_PRESET)
                    df = pd.DataFrame(np.transpose(data))
                    # print('Data From the Board')
                    print(f'Size of data {data.size}')
                    print(df.head(5))
                    DataFilter.write_file(data, str(DATA_DIR / 'ppg_raw.csv'), 'a')
                    # DataFilter.write_file(df, 'data/ppg_tranpose.csv', 'a')

                # print(f'{datetime.datetime.now()} Fetching Data from the Buffer...')
                # data = self.board.get_board_data(preset=BrainFlowPresets.ANCILLARY_PRESET)
                print(f'{datetime.datetime.now()} Stop Streaming...')
                self.board.stop_stream()
                print(f"PPG Sample Rate: {self.ppg_sample_rate}")
                for key, value in self.ppg_board_desc.items():
                    print(f'{key}: {value}')
                # df = pd.DataFrame(np.transpose(data))
                # print('Data From the Board')
                # print(df.head(5))

                # self.board.release_session()
                self.disconnect()
                break

    def disconnect(self):
        print(f'{datetime.datetime.now()} Disconencting from Board...')
        self.board.release_session()
        self.conn = False
        self.stopped = True
        print(f'{datetime.datetime.now()} Disconencted from Board...')


BoardShim.disable_board_logger()
DataFilter.disable_data_logger()

bd = PpgStream()
bd.start()
bd.stop()

if bd.conn:
    bd.disconnect()
