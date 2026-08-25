import cv2
# import logging as log
# import datetime as dt
from time import sleep, time

# https://www.geeksforgeeks.org/python-check-if-list-is-strictly-increasing/
cascPath = "cascades/haarcascades/haarcascade_frontalface_default.xml"
cascPath2 = "cascades/haarcascades/haarcascade_eye.xml"
cascPath3 = "cascades/haarcascades/haarcascade_eye_tree_eyeglasses.xml"
glasses = False
totalBlinks = 0
'''
Add eye_tree_eyeglasses(if no eyes detected check tree_eyeglasses)
use eye_2splits to detect closed eyes?
'''
faceCascade = cv2.CascadeClassifier(cascPath)
eyesCascade = cv2.CascadeClassifier(cascPath2)
# log.basicConfig(filename='webcam.log',level=log.INFO)

video_capture = cv2.VideoCapture(0)
first_read = True
'''min = 2
previous = 0
current = 0
increase = False'''
while True:
    try:
        while not video_capture.isOpened():
            print('Unable to load camera. Ctrl + C to cancel')
            sleep(3)
    except (KeyboardInterrupt):
        video_capture.release()
        print("Program closed")

    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.bilateralFilter(cv2.cvtColor(
        frame, cv2.COLOR_BGR2GRAY), 5, 75, 75)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(20, 20)
    )
    if (len(faces) >= 1):
        (x, y, w, h) = faces[0]
        frame = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        face = gray[y:y+h, x:x+w]

        eyes = eyesCascade.detectMultiScale(
            face,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(5, 5)
        )
        if (len(eyes) >= 2):

                # Check if program is running for detection

                if (first_read):

                    cv2.putText(frame,

                                "Eye detected press s to begin",

                                (70, 70),

                                cv2.FONT_HERSHEY_PLAIN, 3,

                                (0, 255, 0), 2)

                else:

                    cv2.putText(frame,

                                "Eyes open!", (70, 70),

                                cv2.FONT_HERSHEY_PLAIN, 2,

                                (255, 255, 255), 2)

        else:

                if (first_read):

                    # To ensure if the eyes are present before starting

                    cv2.putText(frame,

                                "No eyes detected", (70, 70),

                                cv2.FONT_HERSHEY_PLAIN, 3,

                                (0, 0, 255), 2)

                else:

                    # This will print on console and restart the algorithm

                    print("Blink detected--------------")
                    totalBlinks+=1

                    cv2.waitKey(3000)

                    first_read = True

        # Draw a rectangle around the eyes

        '''num_eyes = len(eyes)
        #print(num_eyes, potential)
        if (num_eyes == 0):
            potential = True
        if (potential and num_eyes == 2):
            print("blink")
            potential = False'''

    # Display the resulting frame
    cv2.imshow('Glasses off - Press 1 to Change mode', frame)
    #if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break
    a = cv2.waitKey(1)

    if (a == ord('q')):

        break

    elif (a == ord('s') and first_read):

        # This will start the detection

        first_read = False
    '''
    if cv2.waitKey(1) & 0xFF == ord('1'):
        if glasses:
            eyesCascade = cascPath2
            cv2.setWindowTitle(
                'Glasses on - Press 1 to Change mode', 'Glasses off - Press 1 to Change mode')
        else:
            eyesCascade =  cascPath3
            cv2.setWindowTitle(
                'Glasses off - Press 1 to Change mode', 'Glasses on - Press 1 to Change mode')
    '''

    # print(time()-t1)

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
