class CameraThread(QThread):
    checkBlink = pyqtSignal()
    changePixmap = pyqtSignal(QImage)
    changeData = pyqtSignal(float, float)
    changeAvgBlink = pyqtSignal(float)
    changeWorkTime = pyqtSignal(float)

    def alert_blink(self):
        print("Please Blink!!")
        # toaster = ToastNotifier()
        # toaster.show_toast("Blink!!!",
        #                 "Please blink your eyes!",
        #                 icon_path='img/eye_warning.ico' ,
        #                 duration=10, threaded=True)
        # TODO

    def alert_work_time(self):
        print("Please take a break!!")
        # toaster = ToastNotifier()
        # toaster.show_toast("Break!!!",
        #                 "Please take a break!",
        #                 icon_path='img/sit_warning.ico' ,
        #                 duration=10, threaded=True)
        # TODO

    def notice_empty_seat(self):
        print("Can't detect face!")
        # TODO

    def run(self):
        # cap = cv2.VideoCapture(0)
        # while True:
        #     ret, frame = cap.read()
        #     if ret:
        #         rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #         convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
        #         p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        #         self.changePixmap.emit(p)

        EYE_AR_CONSEC_FRAMES = args['frames']

        BLINK_ALERT_THRESH = 3  # if LATE_BLINK_CNT is over than this value, system will alert to user.
        WORK_ALERT_THRESH = 3600  # if WORKING_TIME is over than this value, system will alert to user.
        BLINK_GAP_THRESH = 3.0  # if blink-to-blink gap is over than this value, LATE_BLINK_CNT++.
        EMPTY_NOTICE_THRESH = 5  # if user's empty time is over than this value, system will notice.
        LATE_BLINK_CNT = 0
        AVG_BLINK_CNT = 0.0

        # initialize the frame counters and the total number of blinks
        WORKING_TIME = 0
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
                    # print("aaaaa")
                    EMPTY_BEFORE_TIME = time.time()

            if FACE_DETECT_FLAG and EMPTY_SEAT_FLAG:
                BEFORE_TIME = time.time()
                EMPTY_SEAT_FLAG = False
                EMPTY_FLAG = False

            if (not EMPTY_FLAG) and EMPTY_SEAT_FLAG and time.time() - EMPTY_BEFORE_TIME >= EMPTY_NOTICE_THRESH:
                self.notice_empty_seat()
                # WORKING_TIME = 0.0
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

                # draw face landmakrs
                # for (x, y) in shape:
                #     cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)

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
                    NOW_TIME = time.time()
                    if COUNTER >= EYE_AR_CONSEC_FRAMES and (NOW_TIME - BEFORE_TIME) > 1.0:
                        WORKING_TIME += (NOW_TIME - BEFORE_TIME)
                        if (NOW_TIME - BEFORE_TIME) >= BLINK_GAP_THRESH:
                            LATE_BLINK_CNT += 1
                        else:
                            if LATE_BLINK_CNT > 0:
                                LATE_BLINK_CNT -= 1

                        TOTAL += 1
                        if WORKING_TIME >= 60:
                            AVG_BLINK_CNT = TOTAL * 60 / WORKING_TIME
                        self.checkBlink.emit()
                        print("Blink Gap: ", NOW_TIME - BEFORE_TIME, " / totalWorkTime: ", WORKING_TIME, " / EAR: ",
                              BLINK_EAR,
                              " / lateBlinkCount: ", LATE_BLINK_CNT, " / Blink per Minute: ", AVG_BLINK_CNT)
                        BEFORE_TIME = NOW_TIME

                    # reset the eye frame counter
                    COUNTER = 0

                # draw the total number of blinks on the frame along with
                # the computed eye aspect ratio for the frame
                cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                # cv2.putText(frame, "EAR: {:.2f}".format(ear), (500, 30),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Blink Alert
                if LATE_BLINK_CNT >= BLINK_ALERT_THRESH:
                    self.alert_blink()
                    LATE_BLINK_CNT = 0

                # Working Time Alert
                if WORKING_TIME >= WORK_ALERT_THRESH:
                    self.alert_work_time()
                    WORKING_TIME = 0
                    TOTAL = 0
                    AVG_BLINK_CNT = 0

                self.changeData.emit(AVG_BLINK_CNT, WORKING_TIME)

                # self.changeAvgBlink.emit(AVG_BLINK_CNT)
                # self.changeWorkTime.emit(WORKING_TIME)

            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
            p = convertToQtFormat.scaled(camera_width, camera_height, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)
