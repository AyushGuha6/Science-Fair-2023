import sys, time, datetime
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from imutils.video import VideoStream
import dlib as dlib
from scipy.spatial import distance as dist
import cv2, imutils
from imutils import face_utils
from threading import Thread
import utils
from queue import Queue

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.VBL = QVBoxLayout()

        self.FeedLabel = QLabel()
        self.VBL.addWidget(self.FeedLabel)

        self.Worker1 = Worker1()

        self.Worker1.start()
        time.sleep(1)
        self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
        self.setLayout(self.VBL)

    def ImageUpdateSlot(self, Image):
        self.FeedLabel.setPixmap(QPixmap.fromImage(Image))

    def CancelFeed(self):
        self.Worker1.stop()

class Worker1(QThread):
    ImageUpdate = pyqtSignal(QImage)
    
    # initialize dlib's face detector (HOG-based)
    # and then create the facial landmark predictor
    print("[INFO] loading facial landmark predictor...")
    
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('data/shape_predictor_68_face_landmarks.dat')

    # grab the indexes of the facial landmarks for the left and
    # right eye, respectively
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    filedir = "data"     # data directory
    file_prefix = 'blink'   # filename qualifier
    filePath = "data/blink"
    filename = filedir + '/' + file_prefix + '_'\
    + str(datetime.date.today()) + "-"\
    + str(datetime.datetime.now().strftime("%H.%M.%S"))\
    + '.csv'

    Q = Queue(maxsize=128)

    # # create and start the file writer thread
    writer_thread = Thread(target=utils.file_writer, args=(filename,Q), daemon=True) 

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
    
    def run(self, ear_threshold=0.23, eye_ar_consec_frmes=3):
        self.ThreadActive = True
        self.EYE_AR_THRESH = ear_threshold
        self.EYE_AR_CONSEC_FRAMES = eye_ar_consec_frmes

        # initialize frame counters and the total number of blinks
        self.COUNTER = self.TOTAL = self.STARTTIME = self.TOTTIME = self.LASTEAR = 0

        #vs = VideoStream(src=0).start()

        # start the video stream thread
        print("[INFO] starting video stream thread...")
        print("[INFO] print q to quit...")
        #Capture = cv2.VideoCapture(0)
        self.Capture = VideoStream(src=0).start()
        time.sleep(1.0)
        self.STARTTIME = time.time()
        self.Q.put('TIME,BLINK_CNT,EAR,TIME_ELP,BLNKRATE\n') 

        while self.ThreadActive:
            frame = self.Capture.read()     
            frame = imutils.resize(frame, width=450)        
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
            rects = self.detector(gray, 0)  

            for rect in rects:         
                shape = self.predictor(gray, rect)          
                shape = face_utils.shape_to_np(shape)  

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

            #Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #FlippedImage = cv2.flip(Image, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            FlippedImage = cv2.flip(frame, 1)
            cv2.putText(FlippedImage, "Blinks: {}".format(self.TOTAL), (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 0, 255), 2)
            cv2.putText(FlippedImage, "Time: {}".format(round(time.time() - self.STARTTIME)), (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 0, 255), 2)
            cv2.putText(FlippedImage, "EAR: {:.2f}".format(ear), (300, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 0, 255), 2) 
            FlippedImage = imutils.resize(FlippedImage,width=640)           
            ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
            Pic = ConvertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)

            self.ImageUpdate.emit(Pic)
                
    def stop(self):
        self.ThreadActive = False
        self.Capture.stop()
        #Worker1.Capture.release()
        self.quit()

if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    Root.show()
    sys.exit(App.exec())