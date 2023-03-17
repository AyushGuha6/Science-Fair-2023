# import the necessary packages
import dlib as dlib
from scipy.spatial import distance as dist
import cv2, imutils
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread 
from queue import Queue
import os, datetime, time
import utils
#from muse_stream import MuseStream

class DetectEyeBlink():
    def __init__(self, ear_threshold=0.23, eye_ar_consec_frmes=2) -> None:
        # Variables
        self.EYE_AR_THRESH = ear_threshold
        self.EYE_AR_CONSEC_FRAMES = eye_ar_consec_frmes

        # initialize frame counters and the total number of blinks
        self.COUNTER = self.TOTAL = self.STARTTIME = self.TOTTIME = self.LASTEAR = 0

        # initialize dlib's face detector (HOG-based)
        # and then create the facial landmark predictor
        print("[INFO] loading facial landmark predictor...")
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor('data/shape_predictor_68_face_landmarks.dat')

        # grab the indexes of the facial landmarks for the left and
        # right eye, respectively
        (self.lStart, self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.rStart, self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        self.filedir = "data"     # data directory
        self.file_prefix = 'blink'   # filename qualifier
        self.filePath = "data/blink"
        self.filename = self.filedir + '/' + self.file_prefix + '_'\
        + str(datetime.date.today()) + "-"\
        + str(datetime.datetime.now().strftime("%H.%M.%S"))\
        + '.csv'
    
        # Define Blink Analysis Thread
        self.blinkT = Thread(target=self.detecteyeblink,\
                        args=(),\
                        daemon=True)
        
        # create the shared queue
        self.Q = Queue(maxsize=128)

        # create and start the file writer thread
        self.writer_thread = Thread(target=utils.file_writer, args=(self.filePath,self.Q), daemon=True) 

    def detecteyeblink(self):
        # ### Start EEG & PPG capture
        # print("[INFO] starting EEG stream...")
        # print("[INFO] starting PPG stream...")
    #muse_stream1 = MuseStream()
    #conn = muse_stream1.connDevice()
    #if conn:
    #    muse_stream1.startStream()
    #    muse_stream1.start()
    #else:
    #    exit(0)

        # start the video stream thread
        print("[INFO] starting video stream thread...")
        print("[INFO] print q to quit...")
        vs = VideoStream(src=0).start()
        time.sleep(1.0)
        self.STARTTIME = time.time()
        self.Q.put('TIME,BLINK_CNT,EAR,TIME_ELP,BLNKRATE\n') 

        while True:                     # loop over frames from the video stream
            frame = vs.read()           # Grab frame from threaded video file stream
            frame = imutils.resize(frame, width=450)        # Resize video frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert frame to grayscale channels
            rects = self.detector(gray, 0)   # detect faces in the grayscale frame

            for rect in rects:          # loop over the face detection
                shape = self.predictor(gray, rect)           # determine facial landmarks for face region
                shape = face_utils.shape_to_np(shape)   # Convert facial landmark (x, y)-coordinates to NumPy array

                # extract the left and right eye coordinates, then use the
                # coordinates to compute the eye aspect ratio for both eyes
                leftEye = shape[self.lStart:self.lEnd]
                rightEye = shape[self.rStart:self.rEnd]
                leftEAR = self.eye_aspect_ratio(leftEye)
                rightEAR = self.eye_aspect_ratio(rightEye)

                # average the eye aspect ratio together for both eyes
                ear = (leftEAR + rightEAR) / 2.0

                # compute the convex hull for the left and right eye, then
                # visualize each of the eyes
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

                # check to see if the eye aspect ratio is below the blink
                # threshold, and if so, increment the blink frame counter
                if ear < self.EYE_AR_THRESH:
                    self.COUNTER += 1
                    self.LASTEAR = ear

                # otherwise, the eye aspect ratio is not below the blink
                # threshold
                else:
                    # if the eyes were closed for a sufficient number of
                    # then increment the total number of blinks
                    if self.COUNTER >= self.EYE_AR_CONSEC_FRAMES:
                        self.TOTAL += 1
                        self.TOTTIME = time.time() - self.STARTTIME
                        self.BLKRATE = round((self.TOTAL/self.TOTTIME)*60)
                        self.Q.put(str(datetime.datetime.now()) + ',' \
                            + str(self.TOTAL).rjust(10,' ') + ',' \
                            + str(round(self.LASTEAR,2)) + ',' \
                            + str(round(self.TOTTIME)) + ',' \
                            + str(self.BLKRATE)\
                            + '\n' \
                            )
                        self.LASTEAR = 0         # Reset LASTEAR after printing

                    # reset the eye frame counter
                    self.COUNTER = 0

                # draw the total number of blinks on the frame along with
                # the computed eye aspect ratio for the frame
                cv2.putText(frame, "Blinks: {}".format(self.TOTAL), (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.putText(frame, "Time: {}".format(round(time.time() - self.STARTTIME)), (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # show the frame
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
        #       if conn:
        #           muse_stream1.stop()
        #           muse_stream1.stopStream()
        #           conn = muse_stream1.disconnectDevice()
                self.Q.put(None)
                self.Q.join()
                break

        # do a bit of cleanup
        cv2.destroyAllWindows()
        vs.stop()

    def eye_aspect_ratio(self,eye):
        # compute the euclidean distances between the two sets of
        # vertical eye landmarks (x, y)-coordinates
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])

        # compute the euclidean distance between the horizontal
        # eye landmark (x, y)-coordinates
        C = dist.euclidean(eye[0], eye[3])

        # compute the eye aspect ratio
        #ear = (A + B) / (2.0 * C)
        ear = (A + B) / (2.0 * C)

        # return the eye aspect ratio
        return ear

    # dedicated file writing task
    def file_writer(self,filedir,filename,queue):
        if not os.path.exists(filedir):
            os.mkdir(filedir)

        filepath = filedir + '/' + filename + '_'\
                    + str(datetime.date.today()) + "-"\
                    + str(datetime.datetime.now().strftime("%H.%M.%S"))\
                    + '.csv'
        
        # open the file
        with open(filepath, 'w') as file:
            while True: # run until None is received
                line = queue.get()  # get a line of text from the queue
                
                if line is None:    # check if we are done
                    break           # exit the loop
                file.write(str(line))   # write it to file
                file.flush()        # flush the buffer
                queue.task_done()   # mark the unit of work complete
                #time.sleep(.5)
        queue.task_done()           # mark the exit signal as processed, after the file was closed

    def start(self):
        self.writer_thread.start() 
        self.blinkT.start()

if __name__ == '__main__':
    eyeblink = DetectEyeBlink()
    eyeblink.start()
    time.sleep(30)
