import datetime, time, os
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BrainFlowPresets, BoardIds
from brainflow.data_filter import DataFilter, WindowOperations, DetrendOperations
from threading import Thread
from queue import Queue
import numpy as np
import heartpy as hp
import pandas as pd
from scipy.signal import resample

class MuseStream:
    def __init__(self):
        BoardShim.disable_board_logger()
        DataFilter.disable_data_logger()
        self.params = BrainFlowInputParams()
        self.board = BoardShim(BoardIds.MUSE_2_BOARD, self.params)
        self.board_id = BoardIds.MUSE_2_BOARD.value

        ## EEG Properties
        self.eeg_channels = BoardShim.get_eeg_channels(self.board_id)
        self.eeg_channel = self.eeg_channels[1]
        self.eeg_sampling_rate = BoardShim.get_sampling_rate(BoardIds.MUSE_2_BOARD, BrainFlowPresets.DEFAULT_PRESET)
        self.nfft = DataFilter.get_nearest_power_of_two(self.eeg_sampling_rate)

        ## PPG Properties
        self.ppg_channels = BoardShim.get_ppg_channels(BoardIds.MUSE_2_BOARD,  BrainFlowPresets.ANCILLARY_PRESET)
        self.ppg_sampling_rate = BoardShim.get_sampling_rate(BoardIds.MUSE_2_BOARD, BrainFlowPresets.ANCILLARY_PRESET)

        ## Define Control Variables
        self.conn = False
        self.streaming = False
        self.eeg_stopped = True
        self.ppg_stopped = True 
        self.filedir = 'data'
        self.ppg_header_print = False
        
        #EEG
        self.eeg_file_name = self.filedir + '/eeg_' + str(datetime.date.today())\
                + '-' + str(datetime.datetime.now().strftime("%H.%M.%S"))\
                + '.csv'
        # Define EEG Output Queue for writing to file
        self.EEGQ = Queue(maxsize=128)

        # Define EEG Analysis Thread
        self.eegT = Thread(target=self.analyzeEEG,\
                        args=(self.eeg_channel,self.nfft,self.eeg_sampling_rate),\
                        daemon=True)
        #Define EEG Write Thread
        self.eegWT = Thread(target=self.fileWriter,\
                        args=(self.filedir,self.eeg_file_name,self.EEGQ),\
                        daemon=True)
        ##########
        #PPG
        self.ppg_file_name = self.filedir + '/ppg_' + str(datetime.date.today())\
                + '-' + str(datetime.datetime.now().strftime("%H.%M.%S"))\
                + '.csv'
        self.ppg_raw_file_name = self.filedir + '/ppg_raw_' + str(datetime.date.today())\
                + '-' + str(datetime.datetime.now().strftime("%H.%M.%S"))\
                + '.csv'
        # Define PPG Output Queue
        self.PPGQ = Queue(maxsize=128)

        # Define PPG Analysis Thread
        self.ppgT = Thread(target=self.analyzePPG,\
                        args=(self.ppg_sampling_rate,),\
                        daemon=True)
        #Define PPG Write Thread
        self.ppgWT = Thread(target=self.fileWriter,\
                        args=(self.filedir,self.ppg_file_name,self.PPGQ),\
                        daemon=True)
        
    def logger(self, type, msg):
        print(f'{datetime.datetime.now()} [{type.upper()}] {msg}')

    def connDevice(self):
        if self.conn == False:
            self.logger("Info",'Connecting to Device...')
            try:
                self.board.prepare_session()
                self.logger("info","Successfully connected to Device...")
                self.conn = True
                self.board.config_board('p50')
            except Exception as err:
                self.logger("error",err)
                self.conn = False

        return self.conn
    
    def disconnectDevice(self):
        try:
            self.board.release_session()
            self.logger("Info","Successfully disconnected from Device...")
            self.conn = False
        except Exception as err:
            self.logger("error",err)
            self.conn = False
        return self.conn
    
    def startStream(self):
        if self.conn:
            try:
                self.logger("Info","Starting to Stream...")
                self.board.start_stream()
                self.streaming = True
            except Exception as err:
                self.logger("error","start_stream: " + err)
                self.streaming = False
        else:
            self.logger("error","Board not connecetd...")
            self.streaming = False
            exit(0) 
        return self.streaming

    def stopStream(self):
        if self.streaming:
            try:
                self.board.stop_stream()
                self.logger("info","Successfully stopped streaming...")
                self.streaming = False
            except Exception as err:
                self.logger("error","stopStream:" + str(err))
                self.streaming = False

        return self.streaming

    def analyzeEEG(self,eeg_channel,nfft,sampling_rate):
        self.logger("info","Starting EEG Analysis, eeg_stopped set to " + str(self.eeg_stopped))
        #self.EEGQ.put('                      TIME,     DELTA,     THETA,     ALPHA,      BETA,     GAMMA\n')
        self.EEGQ.put('TIME,DELTA,THETA,ALPHA,BETA,GAMMA\n')
        cnt=0
        while True:
            if self.eeg_stopped is True :
                self.logger("info","Stopping EEG Analysis for eeg_stopped set to True...")
                self.EEGQ.put(None)
                break

            time.sleep(10)
            cnt += 10
            
            try:
                data_default = self.board.get_board_data(preset=BrainFlowPresets.DEFAULT_PRESET)
                DataFilter.detrend(data_default[eeg_channel], DetrendOperations.LINEAR.value)

                psd = DataFilter.get_psd_welch(data_default[eeg_channel], nfft, nfft // 2, sampling_rate, WindowOperations.BLACKMAN_HARRIS.value)

                # calc band power
                delta = DataFilter.get_band_power(psd, 0.5, 4.0)
                theta = DataFilter.get_band_power(psd, 4, 8.0)
                alpha = DataFilter.get_band_power(psd, 8.0, 12.0)
                beta = DataFilter.get_band_power(psd, 12.0, 30.0)
                gamma = DataFilter.get_band_power(psd, 30.0, 50.0)
                self.logger("info","Delta:" + str(round(delta,2)).rjust(10,' ') 
                            + " Theta:" + str(round(theta,2)).rjust(10,' ') 
                            + " Alpha:" + str(round(alpha,2)).rjust(10,' ') 
                            + " Beta:" + str(round(beta,2)).rjust(10,' ') 
                            + " Gamma:" + str(round(gamma,2)).rjust(10,' ')
                            + " T/a:" + str(round(theta/alpha, 2)).rjust(10, ' ')
                            + " T/b:" + str(round(theta/beta, 2)).rjust(10, ' ')
                    )
                # otherwise, ensure the queue has room in it
                if not self.EEGQ.full():
                    self.EEGQ.put(str(datetime.datetime.now())\
                        + "," + str(round(delta,2))  \
                        + "," + str(round(theta,2))  \
                        + "," + str(round(alpha,2))  \
                        + "," + str(round(beta,2)) \
                        + "," + str(round(gamma,2)) \
                        + "\n"       
                    )
                else:
                    time.sleep(0.1)  # Rest for 10ms, we have a full queue
            except Exception as err:
                self.logger("Error",err)
                
        return self

    def analyzePPG(self,sampling_rate):
        
        self.logger("Info","Starting PPG Analysis...")

        cnt = 0
        while True:
            if self.ppg_stopped is True :
                # release all resources
                # self.PPGQ.put(None)
                break

            data_ppg = self.board.get_board_data(preset=BrainFlowPresets.ANCILLARY_PRESET)
            DataFilter.write_file(data_ppg, self.ppg_raw_file_name , 'a') 
                                   
            time.sleep(5)
            cnt += 5

            if cnt > 60:
                try:
                    self.logger('info','Calculating Heartpy measure....')
                    measures, hr_brainflow, spo2 = self.calculateHR(self.ppg_raw_file_name, sampling_rate)
                    if measures and 40 < measures['bpm'] < 180:
                        print(f'Valid bpm measure....')
                        ppg_header = []
                        ppg_list = []
                        for key in measures.keys():
                            ppg_header.append('%s' %key)
                            ppg_list.append('%.2f' %(measures[key]))
                    
                        if self.ppg_header_print == False:
                            self.PPGQ.put('TIME,' + (','.join(ppg_header)).upper() + 'HR_BRAINFLOW,SPO2\n')
                            self.ppg_header_print = True
                    
                        if not self.PPGQ.full():
                            hp_output = ','.join(ppg_list)
                            self.PPGQ.put(str(datetime.datetime.now())\
                                + ',' + hp_output \
                                + ',' + str(round(hr_brainflow  ))\
                                + ',' + str(round(spo2)) + '\n')
                            self.logger('info',str(datetime.datetime.now())\
                                + ',' + hp_output \
                                + ',' + str(round(hr_brainflow  ))\
                                + ',' + str(round(spo2)))
                        else:
                            time.sleep(0.1)  # Rest for 10ms, we have a full queue   
                    else:
                        cnt = 0                 
                except Exception as err:
                    self.logger("Error",err)
                    pass

        return self

    def reject_outliers(self, data, m = 2.):
        d = np.abs(data - np.median(data))
        mdev = np.median(d)
        s = d/mdev if mdev else np.zero(len(d))
        return data[s<m]

    def calculateHR(self, ppg_raw_file_name, sample_rate):
        data = DataFilter.read_file(ppg_raw_file_name)
        data = pd.DataFrame(np.transpose(data),
                columns =['package_num_chnl', 'ppg_red', 'ppg_ir','ppg_amb','time','marker'])
        #load PPG RED and IR data and convert to numpy array
        ppg_red=data['ppg_red'].to_numpy()
        ppg_ir=data['ppg_ir'].to_numpy()
        #dtime = data[time].to_numpy()

        if ppg_ir.size > 19200:
            str_point = ppg_ir.size - 19200
            #str_time = datetime.datetime.fromtimestamp(dtime[str_point])
        else:
            str_point = 0

        #hrdata_heartpy = self.reject_outliers(ppg_red[str_point:])
        hr_data_red = ppg_red[str_point:]
        hr_data_ir  = ppg_ir[str_point:]
        data = hr_data_ir
        #calculating HR with Brainflow
        try:
            hr_brainflow = DataFilter.get_heart_rate(hr_data_ir, hr_data_red, sample_rate, 2048) 
        except:
            hr_brainflow = 0
        
        try:
            spo2 = DataFilter.get_oxygen_level(ppg_ir[str_point:], ppg_red[str_point:], sample_rate)
        except:
            spo2 = 0
        
        # calculating HR with HeartPy    
        measures = {}
        working_data = {}

        filtered_ppg = hp.filter_signal(data, cutoff = [0.8, 2.5], filtertype = 'bandpass',
                            sample_rate = sample_rate, order = 3, return_top = False)
        resampled_signal = resample(filtered_ppg, round(len(filtered_ppg) * (100/64)))
        new_sample_rate = 100

        try: 
            working_data, measures = hp.process(hp.scale_data(resampled_signal), sample_rate=new_sample_rate,
                        high_precision = True, clean_rr = True)
            self.logger('info','Completed calc_hr func...')
        except:
            self.logger('Error','Failed to complete calc_hr func...')
            pass
        
        return measures, hr_brainflow, spo2

    def fileWriter(self,file_dir, file_name, queue):
        self.filedir = file_dir
        file_name = file_name
        
        if not os.path.exists(self.filedir):
            os.mkdir(self.filedir)

        # open the file
        with open(file_name, 'w') as file:
            # run until the event is set
            while True:
                # get a line of text from the queue
                line = queue.get()
                
                # check if we are done
                if line is None:
                    # exit the loop
                    self.logger("info","Exiting Writing due to None in Queue...")
                    break
                # write it to file
                file.write(str(line))
                # flush the buffer
                file.flush()
                # mark the unit of work complete
                queue.task_done()
                time.sleep(.5)
        # mark the exit signal as processed, after the file was closed
        queue.task_done()
        return self

    def start(self):
        # method for starting the thread for grabbing next available frame in input stream 
        self.eeg_stopped = False
        self.logger("info","Starting thread eegT...")
        self.eegT.start()
        self.logger("info","Starting thread eegWT...")
        self.eegWT.start() 

        self.ppg_stopped = False
        self.logger("info","Starting thread ppgT...")
        self.ppgT.start()
        self.logger("info","Starting thread ppgWT...")
        self.ppgWT.start() 
        return self 

    def stop(self):
        # method called to stop thread 
        self.eeg_stopped = True
        self.ppg_stopped = True
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.logger("info","Wait for eegT to finish..")
        self.eegT.join() 

        self.logger("info","Wait for ppgT to finish..")
        self.ppgT.join() 

        self.logger("info","Wait for PPGQ to finish..")
        self.PPGQ.join()
        return self