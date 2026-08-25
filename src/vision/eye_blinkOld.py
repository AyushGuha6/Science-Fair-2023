
import dlib as dlib
from scipy.spatial import distance as dist
import cv2
import imutils
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
from queue import Queue
import os
import datetime
import time
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from sensors.muse_stream import MuseStream

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def eye_aspect_ratio(eye):
    '''
    Calculate EAR
    '''
    a = dist.euclidean(eye[1], eye[5])
    b = dist.euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    c = dist.euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (a + b) / (2.0 * c)

    # return the eye aspect ratio
    return ear


def file_writer(filedir, filename, queue):
    '''
    Writes from Queue
    '''
    if not os.path.exists(filedir):
        os.mkdir(filedir)

    filepath = filedir + '/' + filename + '_'\
        + str(datetime.date.today()) + "-"\
        + str(datetime.datetime.now().strftime("%H.%M.%S"))\
        + '.csv'

    with open(filepath, 'w') as file:
        while True:  
            line = queue.get()  # get a line of text from the queue

            if line is None:    # if none then we are done
                break        
            file.write(str(line))   # write it to file
            file.flush()        # flush the buffer
            queue.task_done()   # mark the unit of work complete
            time.sleep(.5)
    queue.task_done()           # mark the exit signal as processed, after the file was closed


def main():
    # Variables
    EYE_AR_THRESH = 0.23
    EYE_AR_CONSEC_FRAMES = 2

    # initialize frame counters and the total number of blinks
    counter = 0
    total = 0
    START_TIME = 0
    totalTime = 0
    blinkRate = 0
    lastEAR = 0

    # initialize dlib's face detector (HOG-based)
    # and then create the facial landmark predictor
    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(str(DATA_DIR / 'shape_predictor_68_face_landmarks_GTX.dat'))

    # grab the indexes of the facial landmarks for the left and
    # right eye, respectively
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    # create the shared queue
    writeQueue = Queue(maxsize=128)
    writeQueue.put('                      TIME, BLINK_CNT,  EAR, TIME_ELP, BLNKRATE\n')

    filedir = str(DATA_DIR)     # data directory
    filename = 'blink'   # filename qualifier

    # create and start the file writer thread
    writer_thread = Thread(target=file_writer, args=(filedir, filename, writeQueue), daemon=True)
    writer_thread.start()
    '''
    # Start EEG & PPG capture
    print("[INFO] starting EEG stream...")
    print("[INFO] starting PPG stream...")
    eeg_stream = MuseStream()
    conn = eeg_stream.connDevice()
    if conn:
        eeg_stream.startStream()
        eeg_stream.start()
    else: 
        exit(0)
    '''

    # start the video stream thread
    print("[INFO] starting video stream thread...")
    print("[INFO] print q to quit...")

    vs = VideoStream(src=0).start()
    time.sleep(1.0)
    START_TIME = time.time()

    while True:                     # loop over frames from the video stream
        frame = vs.read()           # Grab frame from threaded video file stream
        frame = imutils.resize(frame, width=450)        # Resize video frame
        # Convert frame to grayscale channels
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)   # detect faces in the grayscale frame

        for rect in rects:          # loop over the face detection
            # determine facial landmarks for face region
            shape = predictor(gray, rect)
            # Convert facial landmark (x, y)-coordinates to NumPy array
            shape = face_utils.shape_to_np(shape)

            # extract the left and right eye coordinates, then use the
            # coordinates to compute the eye aspect ratio for both eyes
            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

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
            if ear < EYE_AR_THRESH:
                counter += 1
                lastEAR = ear

            # otherwise, the eye aspect ratio is not below the blink
            # threshold
            else:
                # if the eyes were closed for a sufficient number of
                # then increment the total number of blinks
                if counter >= EYE_AR_CONSEC_FRAMES:
                    total += 1
                    totalTime = time.time() - START_TIME
                    blinkRate = round((total/totalTime)*60)
                    writeQueue.put(str(datetime.datetime.now()) + ','
                          + str(total).rjust(10, ' ') + ','
                          + str(round(lastEAR, 2)).rjust(5, ' ') + ','
                          + str(round(totalTime)).rjust(9, ' ') + ','
                          + str(blinkRate).rjust(9, ' ')
                          + '\n'
                          )
                    lastEAR = 0         # Reset LASTEAR after printing

                # reset the eye frame counter
                counter = 0

            # draw the total number of blinks on the frame along with
            # the computed eye aspect ratio for the frame
            cv2.putText(frame, "Blinks: {}".format(total), (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.putText(frame, "Time: {}".format(round(time.time() - START_TIME)), (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            if conn:
                cv2.destroyAllWindows()
                #eeg_stream.stop()
                #eeg_stream.stopStream()
                #conn = eeg_stream.disconnectDevice()
            writeQueue.put(None)
            writeQueue.join()
            break

    # do a bit of cleanup
    # cv2.destroyAllWindows()
    vs.stop()
    print("Closed")


if __name__ == '__main__':
    main()
