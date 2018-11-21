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

from PyQt5.QtCore import (QFile, QTextStream, Qt, QThread, pyqtSignal)
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
 
# construct the argument parse and parse the arguments

def arg():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--shape-predictor",default="shape_predictor_68_face_landmarks.dat",
    	help="path to facial landmark predictor")
    ap.add_argument("-v", "--video", type=str, default="camera",
    	help="path to input video file")
    ap.add_argument("-t", "--threshold", type = float, default=0.27,
    	help="threshold to determine closed eyes")
    ap.add_argument("-f", "--frames", type = int, default=2,
    	help="the number of consecutive frames the eye must be below the threshold")
    return ap

class TitleBar(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.minimize=QToolButton(self)
        self.minimize.setIcon(QIcon('img/min.png'))
        # self.maximize=QToolButton(self)
        # self.maximize.setIcon(QIcon('img/max.png'))
        close=QToolButton(self)
        close.setIcon(QIcon('img/close.png'))

        self.minimize.setMinimumHeight(10)
        close.setMinimumHeight(10)
        # self.maximize.setMinimumHeight(10)

        label = QLabel(self)
        label.setAlignment(Qt.AlignCenter)
        label.setText("Twinkle")
        self.setWindowTitle("Twinkle")

        hbox = QHBoxLayout(self)
        hbox.addWidget(label)
        hbox.addWidget(self.minimize)
        # hbox.addWidget(self.maximize)
        hbox.addWidget(close)

        # hbox.insertStretch(1,500)
        hbox.setSpacing(1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.maxNormal=False
        close.clicked.connect(self.closeFrame)
        self.minimize.clicked.connect(self.showSmall)
        # self.maximize.clicked.connect(self.showMaxRestore)

    def showSmall(self):
        mainFrame.showMinimized()

    def closeFrame(self):
        mainFrame.close()
        # mainFrame.hide()

    # def showMaxRestore(self):
    #     if(self.maxNormal):
    #         mainFrame.showNormal()
    #         self.maxNormal = False
    #         self.maximize.setIcon(QIcon('img/max.png'))
    #     else:
    #         mainFrame.showMaximized()
    #         self.maxNormal = True
    #         self.maximize.setIcon(QIcon('img/max2.png'))            

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
        self.m_content= Content(self)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.m_titleBar)
        vbox.addWidget(self.m_content)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        # layout = QVBoxLayout()
        # layout.addWidget(self.m_content)

        # layout.setContentsMargins(5, 5, 5, 5)
        # layout.setSpacing(0)
        # vbox.addLayout(layout)        

    def mousePressEvent(self,event):
        self.m_old_pos = event.pos()
        self.m_mouse_down = event.button() == Qt.LeftButton

    def mouseMoveEvent(self,event):
        x=event.x()
        y=event.y()

    def mouseReleaseEvent(self,event):
        m_mouse_down=False

class Content(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # exitAct = QAction(QIcon('exit.png'), 'Exit', self)        
        # exitAct.setShortcut('Ctrl+Q')
        # exitAct.setStatusTip('Exit application')
        # exitAct.triggered.connect(qApp.quit)

        # menubar = QMenuBar(self)
        # fileMenu = menubar.addMenu('File')
        # fileMenu.addAction(exitAct)     

        # vLayout = QHBoxLayout(self)

        self.label = QLabel(self)
        self.label.move(280, 120)
        self.label.resize(640, 480)
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()

    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))
        

class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        # cap = cv2.VideoCapture(0)
        # while True:
        #     ret, frame = cap.read()
        #     if ret:
        #         rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #         convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
        #         p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
        #         self.changePixmap.emit(p)

        args = vars(arg().parse_args())
        EYE_AR_THRESH = args['threshold']
        EYE_AR_CONSEC_FRAMES = args['frames']

        # initialize the frame counters and the total number of blinks
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
        
            # loop over the face detections
            for rect in rects:
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
                    COUNTER += 1
        
                # otherwise, the eye aspect ratio is not below the blink
                # threshold
                else:
                    # if the eyes were closed for a sufficient number of
                    # then increment the total number of blinks
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        TOTAL += 1
        
                    # reset the eye frame counter
                    COUNTER = 0
        
                # draw the total number of blinks on the frame along with
                # the computed eye aspect ratio for the frame
                cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)

if __name__ == '__main__' :

    toaster = ToastNotifier()
    toaster.show_toast("Hello", "welcome", threaded=True)

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainFrame = Frame()   

    mainFrame.setGeometry(100, 100, 1500, 800)
    mainFrame.show()    

    sys.exit(app.exec_())