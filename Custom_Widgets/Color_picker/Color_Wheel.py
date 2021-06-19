import math

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QColor, QConicalGradient, QLinearGradient, QVector2D, QBrush
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal



class Color_Wheel(QWidget):
    color_wheel_change_single = pyqtSignal(QColor)

    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.style_manage_controller = [widget.Get_style_manage_controller()
                                        for widget in QApplication.topLevelWidgets()
                                        if 'Main_Window' in str(type(widget))][0]

        self.current_color = QColor(0, 0, 0)
        self.select_mode_enum = 'not_selected'
        self.circle_width = 10
        self.circle_color_list = [QColor(255, 0, 0), QColor(255, 255, 0), QColor(0, 255, 0), QColor(0, 255, 255), QColor(0, 0, 255), QColor(255, 0, 255)]

    def Update_h(self, click_pos):
        center_pos = QPoint(self.rect().center())
        orientation_vec = QVector2D(click_pos) - QVector2D(center_pos)
        orientation_vec.normalize()

        angle_radian = math.acos(orientation_vec.x())
        h_value = int(angle_radian * (180 / 3.1415926))
        # 如果点击圆环下半部分
        if click_pos.y() > center_pos.y():
            h_value = 360 - h_value

        h, s, v, _ = self.current_color.getHsv()
        self.current_color.setHsv(h_value, s, v)

    def Update_s_and_v(self, click_pos):
        circle_diameter = min(self.width(), self.height())
        circle_rect = QRect(self.rect().center().x() - circle_diameter / 2,
                            self.rect().center().y() - circle_diameter / 2,
                            circle_diameter, circle_diameter)
        circle_rect.adjust(2, 2, -2, -2)
        circle_rect.adjust(2, 2, -2, -2)
        circle_rect.adjust(self.circle_width, self.circle_width, -self.circle_width, -self.circle_width)
        circle_rect.adjust(2, 2, -2, -2)

        square_width = math.sqrt(2) / 2 * circle_rect.width()
        square_rect = QRect(self.rect().center().x() - square_width / 2,
                            self.rect().center().y() - square_width / 2,
                            square_width, square_width)
        square_rect.adjust(2, 2, -2, -2)

        s_value = min(int((click_pos.x() - square_rect.x()) / square_rect.width() * 255), 255)
        v_value = min(int((square_rect.bottom() - click_pos.y()) / square_rect.height() * 255), 255)
        s_value = max(s_value, 0)
        v_value = max(v_value, 0)

        h, s, v, _ = self.current_color.getHsv()
        self.current_color.setHsv(h, s_value, v_value)

    def Draw_wheel(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        circle_diameter = min(self.width(), self.height())
        circle_rect = QRect(self.rect().center().x() - circle_diameter / 2,
                            self.rect().center().y() - circle_diameter / 2,
                            circle_diameter, circle_diameter)
        circle_rect.adjust(2, 2, -2, -2)

        # 绘制外边框
        painter.setPen(QPen(self.style_manage_controller.Get_board_color()))
        painter.drawEllipse(circle_rect)
        circle_rect.adjust(2, 2, -2, -2)

        # 绘制圆环渐变颜色
        circle_gradient = QConicalGradient(self.rect().center(), 0)
        gap = 1 / len(self.circle_color_list)
        for i in range(len(self.circle_color_list)):
            circle_gradient.setColorAt(gap * i, self.circle_color_list[i])
        circle_gradient.setColorAt(1, self.circle_color_list[0])
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(circle_gradient)
        painter.drawEllipse(circle_rect)
        circle_rect.adjust(self.circle_width, self.circle_width, -self.circle_width, -self.circle_width)

        # 绘制圆环内空白
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.style_manage_controller.Get_base_color()))
        painter.drawEllipse(circle_rect)
        circle_rect.adjust(2, 2, -2, -2)

        # 绘制内边框
        painter.setPen(QPen(self.style_manage_controller.Get_board_color()))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(circle_rect)

        # 绘制H选择圆圈
        h, s, v, _ = self.current_color.getHsv()
        choose_ring_color = QColor()
        choose_ring_color.setHsv((h + 180) % 360, 255, 255)
        choose_ring_pen = QPen(choose_ring_color)
        choose_ring_pen.setWidth(2)
        painter.setPen(choose_ring_pen)
        painter.setBrush(Qt.NoBrush)

        ring_pos = QVector2D(math.cos(h / (180 / 3.1415926)),
                             math.sin(h / (180 / 3.1415926)))
        ring_pos.normalize()
        circle_rect.adjust(-2, -2, 2, 2)
        ring_pos *= circle_rect.width() / 2 + self.circle_width / 2
        painter.drawEllipse(QPoint(self.rect().center().x() + ring_pos.x(),
                                   self.rect().center().y() - ring_pos.y()),
                            self.circle_width / 5, self.circle_width / 5)

    def Draw_center_rect(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        circle_diameter = min(self.width(), self.height())
        circle_rect = QRect(self.rect().center().x() - circle_diameter / 2,
                            self.rect().center().y() - circle_diameter / 2,
                            circle_diameter, circle_diameter)
        circle_rect.adjust(2, 2, -2, -2)
        circle_rect.adjust(2, 2, -2, -2)
        circle_rect.adjust(self.circle_width, self.circle_width, -self.circle_width, -self.circle_width)
        circle_rect.adjust(2, 2, -2, -2)

        square_width = math.sqrt(2) / 2 * circle_rect.width()
        square_rect = QRect(self.rect().center().x() - square_width / 2,
                            self.rect().center().y() - square_width / 2,
                            square_width, square_width)
        square_rect.adjust(2, 2, -2, -2)

        # 绘制边框
        painter.setPen(QPen(self.style_manage_controller.Get_board_color()))
        painter.drawRect(square_rect)
        square_rect.adjust(2, 2, -2, -2)

        # 绘制渐变
        painter.setCompositionMode(QPainter.CompositionMode_Multiply)
        h, s, v, _ = self.current_color.getHsv()
        color = QColor()
        color.setHsv(h, 255, 255)
        square_gradient_h = QLinearGradient(square_rect.topLeft(), square_rect.topRight())
        square_gradient_h.setColorAt(0, QColor(255, 255, 255))
        square_gradient_h.setColorAt(1, color)
        painter.fillRect(square_rect, square_gradient_h)

        square_gradient_v = QLinearGradient(square_rect.topLeft(), square_rect.bottomLeft())
        square_gradient_v.setColorAt(0, QColor(255, 255, 255))
        square_gradient_v.setColorAt(1, QColor(0, 0, 0))
        painter.fillRect(square_rect, square_gradient_v)

        # 绘制选中的圈
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        r, g, b, _ = self.current_color.getRgb()
        choose_ring_pen = QPen(QColor(255 - r, 255 - g, 255 - b))
        choose_ring_pen.setWidth(2)

        choose_ring_x = (s / 255) * square_rect.width()
        choose_ring_y = (v / 255) * square_rect.height()
        choose_ring_pos = QPoint(square_rect.bottomLeft().x() + choose_ring_x,
                                 square_rect.bottomLeft().y() - choose_ring_y)
        painter.setPen(choose_ring_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(choose_ring_pos, self.circle_width / 5, self.circle_width / 5)

    def Set_current_color(self, color):
        h, s, v, _ = color.getHsv()
        self.current_color.setHsv(h, s, v)
        self.update()

    def paintEvent(self, event):
        self.Draw_wheel()
        self.Draw_center_rect()

        super().paintEvent(event)

    def resizeEvent(self, event):
        circle_diameter = min(self.width(), self.height())
        self.circle_width = circle_diameter / 8

        super().resizeEvent(event)

    def mousePressEvent(self, event):
        self.select_mode_enum = 'not_selected'
        click_pos = event.pos()

        circle_diameter = min(self.width(), self.height())
        circle_rect = QRect(self.rect().center().x() - circle_diameter / 2,
                            self.rect().center().y() - circle_diameter / 2,
                            circle_diameter, circle_diameter)
        circle_rect.adjust(2, 2, -2, -2)
        circle_rect.adjust(2, 2, -2, -2)

        # 判断是否选中圆环
        Distance = lambda point_1, point_2 : math.sqrt((point_1.x() - point_2.x()) ** 2 + (point_1.y() - point_2.y()) ** 2)
        pos_to_center_len = Distance(self.rect().center(), click_pos)

        circle_outer_radius = self.rect().center().x() - circle_rect.topLeft().x()
        circle_rect.adjust(self.circle_width, self.circle_width, -self.circle_width, -self.circle_width)
        circle_inner_radius = self.rect().center().x() - circle_rect.topLeft().x()
        if circle_inner_radius < pos_to_center_len < circle_outer_radius:
            self.select_mode_enum = 'circle'

        # 判断是否选中中间矩形
        circle_rect.adjust(2, 2, -2, -2)
        square_width = math.sqrt(2) * circle_rect.width() / 2
        square_rect = QRect(circle_rect.center().x() - square_width / 2,
                            circle_rect.center().y() - square_width / 2,
                            square_width, square_width)
        square_rect.adjust(2, 2, -2, -2)
        square_rect.adjust(2, 2, -2, -2)
        if square_rect.contains(click_pos):
            self.select_mode_enum = 'rect'

        if self.select_mode_enum == 'circle':
            self.Update_h(click_pos)
            self.color_wheel_change_single.emit(self.current_color)
            self.update()
        elif self.select_mode_enum == 'rect':
            self.Update_s_and_v(click_pos)
            self.color_wheel_change_single.emit(self.current_color)
            self.update()

    def mouseMoveEvent(self, event):
        click_pos = event.pos()
        if self.select_mode_enum == 'circle':
            self.Update_h(click_pos)
            self.color_wheel_change_single.emit(self.current_color)
            self.update()
        elif self.select_mode_enum == 'rect':
            self.Update_s_and_v(click_pos)
            self.color_wheel_change_single.emit(self.current_color)
            self.update()

    def mouseReleaseEvent(self, event):
        click_pos = event.pos()
        if self.select_mode_enum == 'circle':
            self.Update_h(click_pos)
            self.color_wheel_change_single.emit(self.current_color)
            self.update()
        elif self.select_mode_enum == 'rect':
            self.Update_s_and_v(click_pos)
            self.color_wheel_change_single.emit(self.current_color)
            self.update()

        self.select_mode_enum = 'not_selected'
