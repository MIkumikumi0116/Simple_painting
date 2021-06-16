from PyQt5.QtWidgets import QWidget, QLinearGradient
from PyQt5.QtGui import QPainter, QConicalGradient, QPen
from PyQt5.QtCore import QPoint, Qt, QMouseEvent, QColor, QRect, QVector2D, QPolygon



class Custom_Color_Wheel(QWidget):
    def __init__(self, parent_widget, style_manage_controller):
        super().__init__(parent_widget)
        self.style_manage_controller = style_manage_controller

        self.current_value = 0
        self.min_value = 0
        self.max_value = 255

        self.style_margin = 1
        self.style_handel_width = 12
        self.style_handel_height = 10
        self.style_padding = 4

        self.start_color = QColor(0, 0, 0)
        self.end_color = QColor(255, 0, 0)

        self.select_flag = False
        self.h_value_slider_flag = False
        self.color_list = [QColor(255, 0, 0), QColor(255, 255, 0), QColor(0, 255, 0), QColor(0, 255, 255), QColor(0, 0, 255), QColor(255, 0, 255)]

    def Set_start_color(self, start_color):
        self.start_color = start_color
        self.update()

    def Set_end_color(self, end_color):
        self.end_color = end_color
        self.update()

    def Set_current_value(self, value):
        self.current_value = value
        self.update()

    def Get_current_value(self):
        return self.current_value

    def Set_h_value_slide_flag(self, h_value_slider_flag):
        self.h_value_slider_flag = h_value_slider_flag

    def Pick_value(self, click_pos):
        slider_rect = self.rect().adjusted(self.style_margin + self.style_handel_width / 2 - self.style_padding,
                                           self.style_margin,
                                         -(self.style_margin + self.style_handel_width / 2 - self.style_padding),
                                          -self.style_margin - self.style_handel_height)
        slider_rect = slider_rect.adjusted(self.style_padding, self.style_padding, -self.style_padding, -self.style_padding)

        value = (click_pos.x() - slider_rect.x()) / slider_rect.width() * (self.max_value - self.min_value) + self.min_value
        value = max(value, self.min_value)
        value = min(value, self.max_value)
        self.current_value = value

        self.parent_widget.color_slider_change_single.emit(self, self.current_value)

        self.update()

    def paintEvent(self, painter):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        slider_rect = self.rect().adjusted(self.style_margin + self.style_handel_width / 2 - self.style_padding,
                                           self.style_margin,
                                         -(self.style_margin + self.style_handel_width / 2 - self.style_padding),
                                          -self.style_margin - self.style_handel_height)

        # 绘制边框
        painter.setPen(QPen(QColor(200, 200, 200)))
        painter.drawRoundedRect(slider_rect, 4, 4)

        # 绘制渐变
        slider_rect = slider_rect.adjusted(self.style_padding, self.style_padding, -self.style_padding, -self.style_padding)
        slider_gradient = QLinearGradient(slider_rect.topLeft(), slider_rect.topRight())
        if self.h_value_slider_flag:
            gap = 1 / len(self.color_list)
            for i in range(len(self.color_list)):
                slider_gradient.setColorAt(gap * i, self.color_list[i])
            slider_gradient.setColorAt(1, self.color_list[0])
        else:
            slider_gradient.setColorAt(0, start_color)
            slider_gradient.setColorAt(1, end_color)

        painter.setPen(Qt.NoPen)
        painter.setBrush(slider_gradient)
        painter.drawRoundedRect(slider_rect, 4, 4)

        # 绘制滑动手柄
        painter.setBrush(QColor(220, 220, 220))
        handle_pos = self.current_value / (self.max_value - self.min_value) * slider_rect.width() + slider_rect.x()
        handle_pos = QPoint(handle_pos, slider_rect.bottom() + self.style_padding + 1)
        polygon = QPolygon()
        polygon.append(handle_pos)
        polygon.append(QPoint(handle_pos.x() - self.style_handel_width / 2, handle_pos.y() + self.style_handel_height))
        polygon.append(QPoint(handle_pos.x() + self.style_handel_width / 2, handle_pos.y() + self.style_handel_height))
        painter.drawPolygon(polygon)

    def mousePressEvent(self, event):
        click_pos = event.pos

        slider_rect = self.rect().adjusted(self.style_margin + self.style_handel_width / 2 - self.style_padding,
                                           self.style_margin,
                                         -(self.style_margin + self.style_handel_width / 2 - self.style_padding),
                                          -self.style_margin - self.style_handel_height)
        slider_rect = slider_rect.adjusted(self.style_padding, self.style_padding, -self.style_padding, -self.style_padding)

        handle_pos = self.current_value / (self.max_value - self.min_value) * slider_rect.width() + slider_rect.x()
        handle_pos = QPoint(handle_pos, slider_rect.bottom() + self.style_padding + 1)
        polygon = QPolygon()
        polygon.append(handle_pos)
        polygon.append(QPoint(handle_pos.x() - self.style_handel_width / 2, handle_pos.y() + self.style_handel_height))
        polygon.append(QPoint(handle_pos.x() + self.style_handel_width / 2, handle_pos.y() + self.style_handel_height))

        #判断是否选中
        self.select_flag = False
        if slider_rect.contains(click_pos):
            self.select_flag = True
        elif polygon.containsPoint(click_pos, Qt.OddEvenFill):
            self.select_flag = True

        if self.select_flag:
            self.Pick_value(click_pos)

    def mouseMoveEvent(self, event):
        if self.select_flag:
            click_pos = event.pos
            self.Pick_value(click_pos)

    def mouseReleaseEvent(self, event):
        if self.select_flag:
            click_pos = event.pos
            self.Pick_value(click_pos)

        self.select_flag = False