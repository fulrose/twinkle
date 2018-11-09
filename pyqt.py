import sys
from PyQt5.QtCore import QFile, QTextStream, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon

import qdarkstyle

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()        

    def initUI(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        menubar = QMenuBar(self)
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        # btn = QPushButton('Button', self)

        self.setGeometry(100, 100, 1500, 800)
        self.show()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__' :
    main()