class SystemTrayIcon(QSystemTrayIcon):
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
