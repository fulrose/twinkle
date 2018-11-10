import sys
from PyQt5.QtCore import QFile, QTextStream, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import qdarkstyle

class TitleBar(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.minimize=QToolButton(self)
        self.minimize.setIcon(QIcon('img/min.png'))
        self.maximize=QToolButton(self)
        self.maximize.setIcon(QIcon('img/max.png'))
        close=QToolButton(self)
        close.setIcon(QIcon('img/close.png'))

        self.minimize.setMinimumHeight(10)
        close.setMinimumHeight(10)
        self.maximize.setMinimumHeight(10)

        label = QLabel(self)
        label.setAlignment(Qt.AlignCenter)
        label.setText("Window Title")
        self.setWindowTitle("Window Title")

        hbox = QHBoxLayout(self)
        hbox.addWidget(label)
        hbox.addWidget(self.minimize)
        hbox.addWidget(self.maximize)
        hbox.addWidget(close)

        # hbox.insertStretch(1,500)
        hbox.setSpacing(1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.maxNormal=False
        close.clicked.connect(self.closeFrame)
        self.minimize.clicked.connect(self.showSmall)
        self.maximize.clicked.connect(self.showMaxRestore)

    def showSmall(self):
        mainFrame.showMinimized()

    def closeFrame(self):
        mainFrame.close()

    def showMaxRestore(self):
        if(self.maxNormal):
            mainFrame.showNormal()
            self.maxNormal = False
            self.maximize.setIcon(QIcon('img/max.png'))
        else:
            mainFrame.showMaximized()
            self.maxNormal = True
            self.maximize.setIcon(QIcon('img/max2.png'))            

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
   
        self.col = QColor(100, 200, 0)
        
        btn1 = QPushButton('Button', self)
        btn2 = QPushButton('Button', self)
        btn3 = QPushButton('Button', self)
        btn4 = QPushButton('Button4', self)

        vLayout = QHBoxLayout(self)
        vLayout.addWidget(btn1)
        vLayout.addWidget(btn2)
        vLayout.addWidget(btn3)
        vLayout.addWidget(btn4)

if __name__ == '__main__' :
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainFrame = Frame()

    mainFrame.setGeometry(100, 100, 1500, 800)
    mainFrame.show()

    sys.exit(app.exec_())