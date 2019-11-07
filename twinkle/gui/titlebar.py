class TitleBar(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.minimize = QToolButton(self)
        self.minimize.setIcon(QIcon('img/min.png'))
        self.minimize.setStyleSheet("background-color: rbga(0,0,0,0); ")
        close = QToolButton(self)
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
        self.maxNormal = False
        close.clicked.connect(self.closeFrame)
        self.minimize.clicked.connect(self.showSmall)

    def showSmall(self):
        mainFrame.showMinimized()

    def closeFrame(self):
        # mainFrame.close()
        # toaster = ToastNotifier()
        # toaster.show_toast("Still Running", "Program was minimized to Tray..", icon_path='img/eye-tracking.ico', threaded=True)
        mainFrame.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            mainFrame.moving = True
            mainFrame.offset = event.pos()

    def mouseMoveEvent(self, event):
        if mainFrame.moving: mainFrame.move(event.globalPos() - mainFrame.offset)
