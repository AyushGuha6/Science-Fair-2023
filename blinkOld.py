import cv2


face_cascade = cv2.CascadeClassifier(
    'cascades/haarcascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(
    "cascades/haarcascades/haarcascade_eye.xml")

# Variable store execution state

first_read = True

# Starting the video capture

video_capture = cv2.VideoCapture(0)

ret, frame = video_capture.read()


while (ret):

    ret, frame = video_capture.read()

    # Converting the recorded image to grayscale

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Applying filter to remove impurities

    gray = cv2.bilateralFilter(gray, 5, 1, 1)

    # Detecting the face for region of image to be fed to eye classifier

    faces = face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(20, 20))

    if (len(faces) > 0):

        for (x, y, w, h) in faces:

            frame = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # roi_face is face which is input to eye classifier

            face = gray[y:y+h, x:x+w]

            roi_face_clr = frame[y:y+h, x:x+w]

            eyes = eye_cascade.detectMultiScale(
                face, 1.3, 5, minSize=(10, 10))

            # Examining the length of eyes object for eyes

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

                    cv2.waitKey(3000)

                    first_read = True

    else:

        cv2.putText(frame,

                    "No face detected", (100, 100),

                    cv2.FONT_HERSHEY_PLAIN, 3,

                    (0, 255, 0), 2)

    # Controlling the algorithm with keys

    cv2.imshow('img', frame)

    a = cv2.waitKey(1)

    if (a == ord('q')):

        break

    elif (a == ord('s') and first_read):

        # This will start the detection

        first_read = False

video_capture.release()
cv2.destroyAllWindows()
