from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal



class Board_Label(QLabel):
    resize_signal = pyqtSignal()

    def __init__(self, parent_widget):
        super().__init__(parent_widget)

    def resizeEvent(self, event):
        self.resize_signal.emit()
