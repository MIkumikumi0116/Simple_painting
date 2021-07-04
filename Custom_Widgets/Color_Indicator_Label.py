import math

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, pyqtSignal



class Color_Indicator_Label(QLabel):
    update_color_singal = pyqtSignal()

    def __init__(self, parent_widget):
        super().__init__(parent_widget)

        self.setMaximumSize(40, 40)
        self.setMinimumSize(40, 40)

        self.color = QColor(0, 0, 0)


    def Get_color(self):
        return self.color

    def Set_color(self, color):
        r, g, b, _ = color.getRgb()
        self.color.setRgb(r, g, b)
        self.update()


    def mousePressEvent(self, event):
        rect = self.rect()
        rect.adjust(2, 2, -2, -2)

        if rect.contains(event.pos()):
            self.update_color_singal.emit()
            self.update()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawRect(rect)

        rect.adjust(2, 2, -2, -2)

        painter.setPen(Qt.NoPen)
        painter.setBrush(self.color)
        painter.drawRect(rect)
