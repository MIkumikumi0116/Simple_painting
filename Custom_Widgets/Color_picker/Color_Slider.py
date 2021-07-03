from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QColor, QLinearGradient, QPolygon
from PyQt5.QtCore import Qt, QPoint, pyqtSignal


class Color_Slider(QWidget):
    color_slider_change_singal = pyqtSignal(str, int)

    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.style_manage_controller = [widget.Get_style_manage_controller()
                                        for widget in QApplication.topLevelWidgets()
                                        if 'Main_Window' in str(type(widget))][0]

        self.current_value = 0
        self.min_value = 0
        self.max_value = 255

        self.start_color = QColor(0, 0, 0)
        self.end_color = QColor(255, 0, 0)

        self.slider_type_enum = 'r_slider'
        self.color_list = [QColor(255, 0, 0), QColor(255, 255, 0), QColor(0, 255, 0), QColor(0, 255, 255), QColor(0, 0, 255), QColor(255, 0, 255)]

        self.style_padding = 4
        self.style_margin = 1
        self.style_handel_width = 12
        self.style_handel_height = 10


    def Pick_value(self, click_pos):
        slider_rect = self.rect().adjusted(self.style_margin + self.style_handel_width / 2 - self.style_padding,
                                           self.style_margin,
                                         -(self.style_margin + self.style_handel_width / 2 - self.style_padding),
                                          -self.style_margin - self.style_handel_height)
        slider_rect = slider_rect.adjusted(self.style_padding, self.style_padding, -self.style_padding, -self.style_padding)

        value = round((click_pos.x() - slider_rect.x()) / slider_rect.width() * (self.max_value - self.min_value) + self.min_value)
        value = max(self.min_value, min(value, self.max_value))
        self.current_value = value


    def Set_start_color(self, start_color):
        if self.slider_type_enum in ['s_slider', 'v_slider']:
            h, s, v, _ = start_color.getHsv()
            self.start_color.setHsv(h, s, v)
        elif self.slider_type_enum == 'h_slider':
            pass
        else:
            self.start_color = start_color

        self.update()

    def Set_end_color(self, end_color):
        if self.slider_type_enum in ['s_slider', 'v_slider']:
            h, s, v, _ = end_color.getHsv()
            self.end_color.setHsv(h, s, v)
        elif self.slider_type_enum == 'h_slider':
            pass
        else:
            self.end_color = end_color

        self.update()

    def Set_current_value(self, value):
        self.current_value = value
        self.update()

    def Set_slider_type_enum(self, slider_type_enum):
        self.slider_type_enum = slider_type_enum

        if self.slider_type_enum == 'h_slider':
            self.max_value = 360
        else:
            self.max_value = 255


    def mousePressEvent(self, event):
        click_pos = event.pos()

        self.Pick_value(click_pos)
        self.color_slider_change_singal.emit(self.slider_type_enum, self.current_value)
        self.update()

    def mouseMoveEvent(self, event):
        click_pos = event.pos()

        self.Pick_value(click_pos)
        self.color_slider_change_singal.emit(self.slider_type_enum, self.current_value)
        self.update()

    def mouseReleaseEvent(self, event):
        click_pos = event.pos()

        self.Pick_value(click_pos)
        self.color_slider_change_singal.emit(self.slider_type_enum, self.current_value)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        slider_rect = self.rect().adjusted(self.style_margin + self.style_handel_width / 2 - self.style_padding,
                                           self.style_margin,
                                         -(self.style_margin + self.style_handel_width / 2 - self.style_padding),
                                          -self.style_margin - self.style_handel_height,)

        # 绘制边框
        painter.setPen(QPen(self.style_manage_controller.Get_board_color()))
        painter.drawRoundedRect(slider_rect, 4, 4)

        # 绘制渐变
        slider_rect = slider_rect.adjusted(self.style_padding, self.style_padding, -self.style_padding, -self.style_padding)
        slider_gradient = QLinearGradient(slider_rect.topLeft(), slider_rect.topRight())
        if self.slider_type_enum == 'h_slider':
            gap = 1 / len(self.color_list)
            for i in range(len(self.color_list)):
                slider_gradient.setColorAt(gap * i, self.color_list[i])
            slider_gradient.setColorAt(1, self.color_list[0])
        else:
            slider_gradient.setColorAt(0, self.start_color)
            slider_gradient.setColorAt(1, self.end_color)

        painter.setPen(Qt.NoPen)
        painter.setBrush(slider_gradient)
        painter.drawRoundedRect(slider_rect, 4, 4)

        # 绘制滑动手柄
        handle_pos_x = self.current_value / (self.max_value - self.min_value) * slider_rect.width() + slider_rect.x()
        handle_pos = QPoint(handle_pos_x, slider_rect.bottom() + self.style_padding + 1)
        polygon = QPolygon()
        polygon.append(handle_pos)
        polygon.append(QPoint(handle_pos.x() - self.style_handel_width / 2, handle_pos.y() + self.style_handel_height))
        polygon.append(QPoint(handle_pos.x() + self.style_handel_width / 2, handle_pos.y() + self.style_handel_height))
        painter.setBrush(self.style_manage_controller.Get_board_color())
        painter.drawPolygon(polygon)

        super().paintEvent(event)
