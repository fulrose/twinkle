import sys

from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import imutils
import time
import argparse
import dlib
import cv2

from PyQt5.QtCore import (QFile, QTextStream, Qt, QThread, pyqtSignal, QCoreApplication, QTimer)
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import qdarkstyle
from win10toast import ToastNotifier

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

def load_config():
    
    f = open('threshold_config.txt', 'r')
    t = float(f.readline())
    f.close()
    return t

# file write
def save_config(t):
    f = open("threshold_config.txt", "w")

    f.write(str(t))
    f.close()
 
# construct the argument parse and parse the arguments
def arg():

    # ap = argparse.ArgumentParser()
    # ap.add_argument("-p", "--shape-predictor",default="shape_predictor_68_face_landmarks.dat",
    # 	help="path to facial landmark predictor")
    # ap.add_argument("-v", "--video", type=str, default="camera",
    # 	help="path to input video file")
    # ap.add_argument("-t", "--threshold", type = float, default=0.20,
    # 	help="threshold to determine closed eyes")
    # ap.add_argument("-f", "--frames", type = int, default=2,
    # 	help="the number of consecutive frames the eye must be below the threshold")
    ap = {}
    ap['shape_predictor'] = "shape_predictor_68_face_landmarks.dat"
    ap['video'] = "camera"
    ap['threshold'] = load_config()
    ap['frames'] = 2

    return ap

class TitleBar(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.minimize=QToolButton(self)
        self.minimize.setIcon(QIcon('img/min.png'))
        self.minimize.setStyleSheet("background-color: rbga(0,0,0,0); ")
        close=QToolButton(self)
        close.setIcon(QIcon('img/close.png'))
        close.setStyleSheet("background-color: rbga(0,0,0,0);")

        self.minimize.setMinimumHeight(10)
        close.setMinimumHeight(10)

        label = QLabel(self)
        label.setAlignment(Qt.AlignCenter)
        label.setText("Twinkle")
        self.setWindowTitle("Twinkle")

        hbox = QHBoxLayout(self)
        hbox.addWidget(label)
        hbox.addWidget(self.minimize)
        hbox.addWidget(close)

        # hbox.insertStretch(1,500)
        hbox.setSpacing(1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.maxNormal=False
        close.clicked.connect(self.closeFrame)
        self.minimize.clicked.connect(self.showSmall)

    def showSmall(self):
        mainFrame.showMinimized()

    def closeFrame(self):
        # mainFrame.close()
        toaster = ToastNotifier()
        toaster.show_toast("Still Running", "Program was minimized to Tray..", icon_path='img/eye-tracking.ico', threaded=True)
        mainFrame.hide()          

    def mousePressEvent(self,event):
        if event.button() == Qt.LeftButton:
            mainFrame.moving = True
            mainFrame.offset = event.pos()

    def mouseMoveEvent(self,event):
        if mainFrame.moving: mainFrame.move(event.globalPos()-mainFrame.offset)


class Frame(QFrame):
    def __init__(self):
        super().__init__()
        self.initUI()        

    def initUI(self):
        self.m_mouse_down = False
        self.setFrameShape(QFrame.StyledPanel)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        self.m_titleBar= TitleBar(self)        

        # Setting Layout
        hbox = QHBoxLayout()
        self.camera_btn = QPushButton("Check Camera")
        self.camera_btn.setFixedSize(110,30)
        self.camera_btn.clicked.connect(self.buildPopup)
        hbox.addWidget(self.camera_btn, alignment=Qt.AlignRight)
        hbox.setContentsMargins(0,0,14,0)

        # left Label
        left_label = QLabel()
        left_label.setFixedSize(250, 200)
        left_label.setStyleSheet("background-color: #404040; padding: 5px;")

        left_label_vbox = QVBoxLayout(left_label)
        left_label_title = QLabel("Twinkle")
        left_label_title.setStyleSheet("font-size: 25px; font-weight: bold;")
        left_label_unit = QLabel("Avg.")
        left_label_unit.setStyleSheet("font-size: 20px; ")
        self.left_label_content = QLabel("-")        
        self.left_label_content.setStyleSheet("font-size: 75px; font-weight: bold;")

        left_label_vbox.addWidget(left_label_title, alignment=Qt.AlignTop | Qt.AlignCenter)
        left_label_vbox.addWidget(left_label_unit, alignment=Qt.AlignTop | Qt.AlignCenter)
        left_label_vbox.addWidget(self.left_label_content, alignment=Qt.AlignRight)
    
        # Right Label
        right_label = QLabel()
        right_label.setFixedSize(250,200)
        right_label.setStyleSheet("background-color: #404040; padding: 5px;")

        right_label_vbox = QVBoxLayout(right_label)
        right_label_title = QLabel("Working Time")
        right_label_title.setStyleSheet("font-size: 25px; font-weight: bold;")
        right_label_unit = QLabel("(minute)")
        right_label_unit.setStyleSheet("font-size: 20px;")
        self.right_label_content = QLabel("0")
        self.right_label_content.setStyleSheet("font-size: 75px; font-weight: bold;")

        right_label_vbox.addWidget(right_label_title, alignment=Qt.AlignTop | Qt.AlignCenter)
        right_label_vbox.addWidget(right_label_unit, alignment=Qt.AlignTop | Qt.AlignCenter)
        right_label_vbox.addWidget(self.right_label_content, alignment=Qt.AlignRight)

        # Top label Style
        main_top = QWidget()
        # main_top.setStyleSheet("background-color: gray;")                
        main_hbox = QHBoxLayout(main_top)
        main_hbox.addWidget(left_label, alignment=Qt.AlignCenter)
        main_hbox.addWidget(right_label, alignment=Qt.AlignCenter)

        # Bottom Style
        main_bottom = QHBoxLayout()
        self.blinkImg = QLabel()
        self.blinkImg.setPixmap(QPixmap('img/eye_off.png'))
        th.checkBlink.connect(self.changeBlinkImg)

        bottom_state = QVBoxLayout()
        self.state_title = QLabel("state title")
        self.state_content = QLabel("state content")
        bottom_state.addWidget(self.state_title)        
        bottom_state.addWidget(self.state_content)
        bottom_state.addSpacing(10)
        bottom_state.setAlignment(Qt.AlignLeft)

        main_bottom.addWidget(self.blinkImg, alignment=Qt.AlignCenter)
        main_bottom.addLayout(bottom_state)
        # main_bottom.setAlignment(Qt.AlignCenter)

        th.changeData.connect(self.updateState)

        # Main Layout
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.m_titleBar)
        vbox.addLayout(hbox)
        vbox.addWidget(main_top)
        vbox.addLayout(main_bottom)        
        vbox.setContentsMargins(0, 0, 0, 0) 

    def updateState(self, blink, work):
        blink = round(blink, 1)
        self.left_label_content.setText(str(blink))

        work_min = int(work/60)
        self.right_label_content.setText(str(work_min))

        if ( blink > 20 and work_min < 59 ):
            # State Good
            self.state_title.setText("Good")
            self.state_title.setStyleSheet("font-size: 30px; font-weight: bold; color: #00FA9A;")          
            self.state_content.setText("good state")
            self.state_content.setStyleSheet("font-size: 18px; font-weight: bold;")

        elif ( str(blink) == "0.0" and str(work_min) == "0" ):
            # State Wait 
            self.state_title.setText("Wating")
            self.state_title.setStyleSheet("font-size: 30px; font-weight: bold;")   
            self.state_content.setText("Please Wait")
            self.state_content.setStyleSheet("font-size: 18px; font-weight: bold;")

        elif ( blink > 20 and work_min >= 59 ):
            # State bad ( for work time )
            self.state_title.setText("Bad")
            self.state_title.setStyleSheet("font-size: 30px; font-weight: bold; color: #FFA500;")     
            self.state_content.setText("Stand up")
            self.state_content.setStyleSheet("font-size: 18px; font-weight: bold;")

        elif ( blink <= 20 and work_min < 59 ):
            # State bad ( for blink )
            self.state_title.setText("Bad")
            self.state_title.setStyleSheet("font-size: 30px; font-weight: bold; color: #FFA500;")    
            self.state_content.setText("Close your Eye")
            self.state_content.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        elif ( blink <= 20 and work_min >= 59 ):
            # State Warning 
            self.state_title.setText("Warning")
            self.state_title.setStyleSheet("font-size: 30px; font-weight: bold; color: #FF4500;")   
            self.state_content.setText("Get out here")  
            self.state_content.setStyleSheet("font-size: 18px; font-weight: bold;")      

    def changeBlinkImg(self):
        self.blinkImg.setPixmap(QPixmap('img/eye_on.png'))
        QTimer.singleShot(200, self.eyeOff)       

    def eyeOff(self):
        self.blinkImg.setPixmap(QPixmap('img/eye_off.png'))

    def buildPopup(self):
        self.cameraLabel = QLabel(self)
        th.changePixmap.connect(self.setImage) 
        self.cameraLabel.setGeometry(0, 0, camera_height, camera_height)

        self.tmpThreshold = args['threshold']

        self.popup = CameraPopup(self)
        self.popup.move(800, 100)

        text_sensitive = QLabel("Sensitive")
        text_sensitive.setStyleSheet("font-size: 20px; font-weight: bold;")

        scaleLayout = QHBoxLayout()
        decBtn = QPushButton()
        decBtn.setIcon(QIcon('img/white_minus.ico'))
        decBtn.clicked.connect(self.decThreshold)
        incBtn = QPushButton()
        incBtn.setIcon(QIcon('img/white_plus.ico'))
        incBtn.clicked.connect(self.incThreshold)
        self.thresholdText = QLabel("-")
        self.thresholdText.setStyleSheet("font-size: 30px;")
        self.thresholdText.setText(str(self.tmpThreshold))
        scaleLayout.addWidget(decBtn)
        scaleLayout.addSpacing(30)
        scaleLayout.addWidget(self.thresholdText)
        scaleLayout.addSpacing(30)
        scaleLayout.addWidget(incBtn)
        scaleLayout.setAlignment(Qt.AlignCenter)        

        btnLayout = QHBoxLayout()
        saveBtn = QPushButton("Save Change")
        saveBtn.setFixedSize(100, 30)
        saveBtn.clicked.connect(self.saveThreshold)
        nonSaveCloseBtn = QPushButton("Close")
        nonSaveCloseBtn.setFixedSize(100, 30)
        nonSaveCloseBtn.clicked.connect(self.closePopup)
        btnLayout.addWidget(saveBtn)
        btnLayout.addSpacing(30)
        btnLayout.addWidget(nonSaveCloseBtn)
        btnLayout.setAlignment(Qt.AlignCenter)
            
        vbox = QVBoxLayout(self.popup)
        vbox.addWidget(self.cameraLabel)
        vbox.addSpacing(5)
        vbox.addWidget(text_sensitive, alignment=Qt.AlignCenter)
        vbox.addSpacing(5)
        vbox.addLayout(scaleLayout)
        vbox.addLayout(btnLayout)
        self.popup.show()

    def decThreshold(self):
        self.tmpThreshold -= 0.01
        self.tmpThreshold = round(self.tmpThreshold, 2)
        global EYE_AR_THRESH
        EYE_AR_THRESH = self.tmpThreshold
        self.thresholdText.setText(str(self.tmpThreshold))

    def incThreshold(self):
        self.tmpThreshold += 0.01
        self.tmpThreshold = round(self.tmpThreshold, 2)
        global EYE_AR_THRESH
        EYE_AR_THRESH = self.tmpThreshold
        self.thresholdText.setText(str(self.tmpThreshold))

    def saveThreshold(self):
        save_config(self.tmpThreshold)
        args['threshold'] = self.tmpThreshold
        toaster = ToastNotifier()
        toaster.show_toast("Save", "Save changed", icon_path='img/eye-tracking.ico', threaded=True)
        self.popup.hide()

    def closePopup(self):
        self.tmpThreshold = args['threshold']
        self.popup.hide()

    def setImage(self, image):
        self.cameraLabel.setPixmap(QPixmap.fromImage(image))

    def mousePressEvent(self,event):
        self.m_old_pos = event.pos()
        self.m_mouse_down = event.button() == Qt.LeftButton

    def mouseMoveEvent(self,event):
        x=event.x()
        y=event.y()

    def mouseReleaseEvent(self,event):
        m_mouse_down=False


class CameraPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def closeEvent(self, evnt):
        evnt.ignore()
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()

class CameraThread(QThread):
    checkBlink = pyqtSignal()
    changePixmap = pyqtSignal(QImage)
    changeData = pyqtSignal(float, float)
    changeAvgBlink = pyqtSignal(float)
    changeWorkTime = pyqtSignal(float)

    def alert_blink(self):
        print("Please Blink!!")
        toaster = ToastNotifier()
        toaster.show_toast("Blink!!!",
                        "Please blink your eyes!",
                        icon_path='img/eye_warning.ico' ,
                        duration=10, threaded=True)
        # TODO

    def alert_work_time(self):
        print("Please take a break!!")
        toaster = ToastNotifier()
        toaster.show_toast("Break!!!",
                        "Please take a break!",
                        icon_path='img/sit_warning.ico' ,
                        duration=10, threaded=True)
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
        EMPTY_NOTICE_THRESH = 5 # if user's empty time is over than this value, system will notice.
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
                    #print("aaaaa")
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
                        print("Blink Gap: ", NOW_TIME - BEFORE_TIME, " / totalWorkTime: ", WORKING_TIME, " / EAR: ", BLINK_EAR,
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

class SysetmTrayIcon(QSystemTrayIcon):
    def __init__(self, QIcon, parent=None):
        QSystemTrayIcon.__init__(self, QIcon, parent)

        trayMenu = QMenu()
        openAct = QAction("Open", self)
        openAct.triggered.connect(self.open)

        exitAct = QAction("Exit", self)
        exitAct.triggered.connect(self.exit)

        trayMenu.addAction(openAct)        
        trayMenu.addAction(exitAct)
        
        self.setContextMenu(trayMenu)

    def open(self):
        mainFrame.show()

    def exit(self):
        mainFrame.close()


if __name__ == '__main__' :

    camera_width = 640
    camera_height = 480
    args = arg()
    EYE_AR_THRESH = args['threshold']

    toaster = ToastNotifier()
    toaster.show_toast("Twinkle", "Running...", icon_path='img/eye-tracking.ico' , threaded=True)
    th = CameraThread()
    th.start()
    time.sleep(4.0)

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())    
    mainFrame = Frame()

    # check Camera!
    mainFrame.buildPopup()

    trayIcon = SysetmTrayIcon(QIcon('img/program_icon.png'))
    trayIcon.show()

    mainFrame.setGeometry(100, 100, 550, 450)
    # mainFrame.show()    

    sys.exit(app.exec_())