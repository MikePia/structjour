from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import  QContextMenuEvent

class ClickLabel(QLabel):
    clicked = pyqtSignal(QLabel, QContextMenuEvent)

    def contextMenuEvent(self, event):
        self.clicked.emit(self, event)
        QLabel.contextMenuEvent(self, event)
        # print('got x mouse?', type(event))