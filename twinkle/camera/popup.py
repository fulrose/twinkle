class CameraPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def closeEvent(self, evnt):
        evnt.ignore()
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()
