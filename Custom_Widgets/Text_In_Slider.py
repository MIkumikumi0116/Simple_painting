from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, pyqtSignal



class Text_In_Slider(QWidget):
    value_change_single = pyqtSignal(int)

    def __init__(self,parent_widget):
        super().__init__(parent_widget)
        self.style_manage_controller = [widget.Get_style_manage_controller()
                                        for widget in QApplication.topLevelWidgets()
                                        if 'Main_Window' in str(type(widget))][0]

        self.current_value = 10
        self.min_value = 0
        self.max_value = 100

        self.left_text = '10'
        self.right_text = '90'

    def Set_current_value(self, value):
        self.current_value = value

    def Get_current_value(self):
        return self.current_value

    def Set_min_value(self, value):
        self.min_value = value

    def Set_max_value(self, value):
        self.max_value = value

    def Set_left_text(self, text):
        self.left_text = text

    def Set_right_text(self, text):
        self.right_text = text

    def mousePressEvent(self, event):
        pos = event.pos()

        slider_rect = self.rect()
        slider_rect = slider_rect.adjusted(2, 2, -2, -2)

        value = (pos.x() - slider_rect.x()) / slider_rect.width() * (self.max_value - self.min_value)
        value = min(value, self.max_value)
        value = max(value, self.min_value)
        self.current_value = value

        self.value_change_single.emit(self.current_value)
        self.update()

    def mouseMoveEvent(self, event):
        pos = event.pos()

        slider_rect = self.rect()
        slider_rect = slider_rect.adjusted(2, 2, -2, -2)

        value = (pos.x() - slider_rect.x()) / slider_rect.width() * (self.max_value - self.min_value)
        value = min(value, self.max_value)
        value = max(value, self.min_value)
        self.current_value = value

        self.value_change_single.emit(self.current_value)
        self.update()

    def mouseReleaseEvent(self, event):
        pos = event.pos()

        slider_rect = self.rect()
        slider_rect = slider_rect.adjusted(2, 2, -2, -2)

        value = (pos.x() - slider_rect.x()) / slider_rect.width() * (self.max_value - self.min_value)
        value = min(value, self.max_value)
        value = max(value, self.min_value)
        self.current_value = value

        self.value_change_single.emit(self.current_value)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        slider_rect = self.rect()
        painter.setPen(QPen(self.style_manage_controller.Get_board_color()))
        painter.drawRoundedRect(slider_rect, 2, 2)

        slider_rect.adjust(2, 2, -2, -2)
        gray_rect = slider_rect.adjusted(0, 0, self.current_value / (self.max_value - self.min_value) * slider_rect.width(), 0)
        white_rect = slider_rect.adjusted(self.current_value / (self.max_value - self.min_value) * slider_rect.width(), 0, 0, 0)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(192, 192, 192))
        painter.drawRect(slider_rect)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(white_rect)

        slider_rect.adjust(2, 0, -2, 0)
        painter.setPen(QPen(self.style_manage_controller.Get_text_color()))
        painter.setBrush(Qt.NoBrush)
        painter.drawText(slider_rect, Qt.AlignLeft, self.left_text)
        painter.drawText(slider_rect, Qt.AlignRight, self.right_text)

        super().paintEvent(event)
