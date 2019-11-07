class Frame(QFrame):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.m_mouse_down = False
        self.setFrameShape(QFrame.StyledPanel)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        self.m_titleBar = TitleBar(self)

        # Setting Layout
        hbox = QHBoxLayout()
        self.camera_btn = QPushButton("Check Camera")
        self.camera_btn.setFixedSize(110, 30)
        self.camera_btn.clicked.connect(self.buildPopup)
        hbox.addWidget(self.camera_btn, alignment=Qt.AlignRight)
        hbox.setContentsMargins(0, 0, 14, 0)

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
        right_label.setFixedSize(250, 200)
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

        work_min = int(work / 60)
        self.right_label_content.setText(str(work_min))

        if (blink > 20 and work_min < 59):
            # State Good
            self.state_title.setText("Good")
            self.state_title.setStyleSheet("font-size: 30px; font-weight: bold; color: #00FA9A;")
            self.state_content.setText("good state")
            self.state_content.setStyleSheet("font-size: 18px; font-weight: bold;")

        elif (str(blink) == "0.0" and str(work_min) == "0"):
            # State Wait
            self.state_title.setText("Wating")
            self.state_title.setStyleSheet("font-size: 30px; font-weight: bold;")
            self.state_content.setText("Please Wait")
            self.state_content.setStyleSheet("font-size: 18px; font-weight: bold;")

        elif (blink > 20 and work_min >= 59):
            # State bad ( for work time )
            self.state_title.setText("Bad")
            self.state_title.setStyleSheet("font-size: 30px; font-weight: bold; color: #FFA500;")
            self.state_content.setText("Stand up")
            self.state_content.setStyleSheet("font-size: 18px; font-weight: bold;")

        elif (blink <= 20 and work_min < 59):
            # State bad ( for blink )
            self.state_title.setText("Bad")
            self.state_title.setStyleSheet("font-size: 30px; font-weight: bold; color: #FFA500;")
            self.state_content.setText("Close your Eye")
            self.state_content.setStyleSheet("font-size: 18px; font-weight: bold;")

        elif (blink <= 20 and work_min >= 59):
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
        # toaster = ToastNotifier()
        # toaster.show_toast("Save", "Save changed", icon_path='img/eye-tracking.ico', threaded=True)
        self.popup.hide()

    def closePopup(self):
        self.tmpThreshold = args['threshold']
        self.popup.hide()

    def setImage(self, image):
        self.cameraLabel.setPixmap(QPixmap.fromImage(image))

    def mousePressEvent(self, event):
        self.m_old_pos = event.pos()
        self.m_mouse_down = event.button() == Qt.LeftButton

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()

    def mouseReleaseEvent(self, event):
        m_mouse_down = False
