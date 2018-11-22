# import the necessary packages
from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import argparse
import imutils
import time
import dlib
import cv2


def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])

    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)

    # return the eye aspect ratio
    return ear


# construct the argument parse and parse the arguments

def arg():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--shape-predictor", default="shape_predictor_68_face_landmarks.dat",
                    help="path to facial landmark predictor")
    ap.add_argument("-v", "--video", type=str, default="camera",
                    help="path to input video file")
    ap.add_argument("-t", "--threshold", type=float, default=0.14,
                    help="threshold to determine closed eyes")
    ap.add_argument("-f", "--frames", type=int, default=1,
                    help="the number of consecutive frames the eye must be below the threshold")
    return ap


def alert_blink():
    print("Please Blink!!")
    # TODO


def alert_work_time():
    print("Please take a break!!")
    # TODO


def notice_empty_seat():
    print("Can't detect face!")
    # TODO


def main():
    args = vars(arg().parse_args())
    EYE_AR_THRESH = args['threshold']
    EYE_AR_CONSEC_FRAMES = args['frames']

    BLINK_ALERT_THRESH = 6  # if LATE_BLINK_CNT is over than this value, system will alert to user.
    WORK_ALERT_THRESH = 60  # if WORKING_TIME is over than this value, system will alert to user.
    BLINK_GAP_THRESH = 3.0  # if blink-to-blink gap is over than this value, LATE_BLINK_CNT++.
    EMPTY_NOTICE_THRESH = 5 # if user's empty time is over than this value, system will notice.
    LATE_BLINK_CNT = 0

    # initialize the frame counters and the total number of blinks
    WORKING_TIME = 0.0
    START_FLAG = False
    FACE_DETECT_FLAG = False
    EMPTY_SEAT_FLAG = False
    EMPTY_FLAG = False

    COUNTER = 0
    TOTAL = 0

    # initialize dlib's face detector (HOG-based) and then create
    # the facial landmark predictor
    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(args["shape_predictor"])

    # grab the indexes of the facial landmarks for the left and
    # right eye, respectively
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    # start the video stream thread
    print("[INFO] starting video stream thread...")
    print("[INFO] print q to quit...")
    if args['video'] == "camera":
        vs = VideoStream(src=0).start()
        fileStream = False
    else:
        vs = FileVideoStream(args["video"]).start()
        fileStream = True

    time.sleep(1.0)

    # loop over frames from the video stream
    while True:
        if not START_FLAG:
            BEFORE_TIME = time.time()
        if (not START_FLAG) and FACE_DETECT_FLAG:
            BEFORE_TIME = time.time()
            START_FLAG = True
        if START_FLAG and (not FACE_DETECT_FLAG):
            # BEFORE_TIME = time.time()
            if not EMPTY_SEAT_FLAG:
                EMPTY_SEAT_FLAG = True
                #print("aaaaa")
                EMPTY_BEFORE_TIME = time.time()

        if FACE_DETECT_FLAG and EMPTY_SEAT_FLAG:
            BEFORE_TIME = time.time()
            EMPTY_SEAT_FLAG = False
            EMPTY_FLAG = False

        if (not EMPTY_FLAG) and EMPTY_SEAT_FLAG and time.time() - EMPTY_BEFORE_TIME >= EMPTY_NOTICE_THRESH:
            notice_empty_seat()
            WORKING_TIME = 0.0
            EMPTY_FLAG = True

        # if this is a file video stream, then we need to check if
        # there any more frames left in the buffer to process
        if fileStream and not vs.more():
            break

        # grab the frame from the threaded video file stream, resize
        # it, and convert it to grayscale
        # channels)
        frame = vs.read()
        frame = imutils.resize(frame, width=640)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detect faces in the grayscale frame
        rects = detector(gray, 0)
        FACE_DETECT_FLAG = False
        # loop over the face detections
        for rect in rects:
            FACE_DETECT_FLAG = True
            # print("test.....")
            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy
            # array
            shape = predictor(gray, rect)
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
                BLINK_EAR = ear
                COUNTER += 1

            # otherwise, the eye aspect ratio is not below the blink
            # threshold
            else:
                # if the eyes were closed for a sufficient number of
                # then increment the total number of blinks
                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    NOW_TIME = time.time()
                    WORKING_TIME += (NOW_TIME - BEFORE_TIME)
                    if (NOW_TIME - BEFORE_TIME) >= BLINK_GAP_THRESH:
                        LATE_BLINK_CNT += 1
                    else:
                        if LATE_BLINK_CNT > 0:
                            LATE_BLINK_CNT -= 1
                    print("Blink Gap: ", NOW_TIME - BEFORE_TIME, " / totalWorkTime: ", WORKING_TIME, " / EAR: ", BLINK_EAR,
                          " / lateBlinkCount: ", LATE_BLINK_CNT)
                    BEFORE_TIME = NOW_TIME
                    TOTAL += 1

                # reset the eye frame counter
                COUNTER = 0

            # draw the total number of blinks on the frame along with
            # the computed eye aspect ratio for the frame
            cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "EAR: {:.2f}".format(ear), (500, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Blink Alert
            if LATE_BLINK_CNT >= BLINK_ALERT_THRESH:
                alert_blink()
                LATE_BLINK_CNT = 0

            # Working Time Alert
            if WORKING_TIME >= WORK_ALERT_THRESH:
                alert_work_time()
                WORKING_TIME = 0

        # show the frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()

if __name__ == '__main__':
    main()