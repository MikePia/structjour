from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal

class ClickLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        QLabel.mousePressEvent(self, event)
        print('got mouse?')