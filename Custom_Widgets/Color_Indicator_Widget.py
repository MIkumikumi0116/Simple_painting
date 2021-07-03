import math

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPolygonF
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal



class Color_Indicator_Widget(QWidget):
    switch_color_singal = pyqtSignal()

    def __init__(self, parent_widget):
        super().__init__(parent_widget)

        self.setMaximumSize(70, 70)
        self.setMinimumSize(70, 70)
        self.setMouseTracking(True)

        self.mouse_clicked_flag = False
        self.mouse_in_flag = False

        self.front_color = QColor(255, 0, 0)
        self.back_color  = QColor(0, 255, 0)

    def Set_front_color(self, color):
        r, g, b, _ = color.getRgb()
        self.front_color.setRgb(r, g, b)
        self.update()

    def Set_back_color(self, color):
        r, g, b, _ = color.getRgb()
        self.back_color.setRgb(r, g, b)
        self.update()


    def mousePressEvent(self, event):
        if QRect(43, 6, 21, 21).contains(event.pos()):
            self.mouse_clicked_flag = True
            self.update()

    def mouseMoveEvent(self, event):
        if QRect(43, 6, 21, 21).contains(event.pos()):
            self.mouse_in_flag = True
        else:
            self.mouse_in_flag = False

        self.update()

    def mouseReleaseEvent(self, event):
        if QRect(43, 6, 21, 21).contains(event.pos()):
            self.switch_color_singal.emit()

        self.mouse_clicked_flag = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setBrush(Qt.NoBrush)
        back_color_rect = QRect(29, 31, 35, 35)
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawRect(back_color_rect)

        back_color_rect.adjust(1, 1, -1, -1)
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawRect(back_color_rect)

        back_color_rect.adjust(1, 1, 0, 0)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.back_color))
        painter.drawRect(back_color_rect)


        painter.setBrush(Qt.NoBrush)
        front_color_rect = QRect(4, 6, 35, 35)
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawRect(front_color_rect)

        front_color_rect.adjust(1, 1, -1, -1)
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawRect(front_color_rect)

        front_color_rect.adjust(1, 1, 0, 0)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.front_color))
        painter.drawRect(front_color_rect)


        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(44, 13, 14, 14, 0, 90*16)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0))
        point_list = [QPoint(51, 9), QPoint(51, 19), QPoint(46, 13)]
        painter.drawPolygon(QPolygonF(point_list))
        point_list = [QPoint(52, 20), QPoint(62, 20), QPoint(58, 25)]
        painter.drawPolygon(QPolygonF(point_list))

        if self.mouse_clicked_flag:
            painter.setPen(QPen(QColor(0, 0, 0, 150)))
            painter.setBrush(QBrush(QColor(0, 0, 0, 96)))
            painter.drawRoundedRect(QRect(43, 6, 21, 21), 2, 2)
        else:
            if self.mouse_in_flag:
                painter.setPen(QPen(QColor(0, 0, 0, 128)))
                painter.setBrush(QBrush(QColor(0, 0, 0, 48)))
                painter.drawRoundedRect(QRect(43, 6, 21, 21), 2, 2)
