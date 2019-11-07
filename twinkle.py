import sys
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import imutils
import time

import dlib
import cv2

from PyQt5.QtCore import (QFile, QTextStream, Qt, QThread, pyqtSignal, QCoreApplication, QTimer)
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import qdarkstyle

if __name__ == '__main__':

    camera_width = 640
    camera_height = 480
    args = arg()
    EYE_AR_THRESH = args['threshold']

    # toaster = ToastNotifier()
    # toaster.show_toast("Twinkle", "Running...", icon_path='img/eye-tracking.ico' , threaded=True)
    th = CameraThread()
    th.start()
    time.sleep(4.0)

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())    
    mainFrame = Frame()

    # check Camera!
    mainFrame.buildPopup()

    trayIcon = SystemTrayIcon(QIcon('img/program_icon.png'))
    trayIcon.show()

    mainFrame.setGeometry(100, 100, 550, 450)
    # mainFrame.show()    

    sys.exit(app.exec_())