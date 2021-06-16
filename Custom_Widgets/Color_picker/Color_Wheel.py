import math
import copy

from PyQt5.QtWidgets import QWidget, QLinearGradient
from PyQt5.QtGui import QPainter, QConicalGradient, QPen
from PyQt5.QtCore import QPoint, Qt, QMouseEvent, QColor, QRect, QVector2D



class Custom_Color_Wheel(QWidget):
    def __init__(self, parent_widget, style_manage_controller):
        super().__init__(parent_widget)
        self.style_manage_controller = style_manage_controller  # TODO

        # self.parent_widget.color_wheel_changed.emit()         # TODO这里没有这句，写着只是别忘了
        self.current_color = QColor(0, 0, 0)
        self.select_mode_enum = 'normal'
        self.circle_width = 10
        self.circle_color_list = [QColor(255, 0, 0), QColor(255, 255, 0), QColor(0, 255, 0), QColor(0, 255, 255), QColor(0, 0, 255), QColor(255, 0, 255)]

    def Get_current_color(self):
        return self.current_color

    def Set_current_color(self, color):
        self.current_color = copy.deepcopy(color)

        self.update()

    def Distance(self, point_1, point_2):
        return math.sqrt((point_1.x() - point_2.x()) ** 2 + (point_1.y() - point_2.y()) ** 2)

    def Update_h(self, click_pos):
        center_pos = QPoint(self.rect().center())
        orientation_vec = QVector2D(click_pos) - QVector2D(center_pos)
        orientation_vec.normalize()

        angle_radian = math.acos(orientation_vec.x())
        h_value = angle_radian * (180 / 3.1415926)
        # 如果点击圆环下半部分
        if click_pos.y() > center_pos.y():
            h_value = 360 - h_value

        h, s, v = self.current_color.getHsv()
        self.current_color.setHsv(h_value, s, v)

    def Update_s_and_v(self, click_pos):
        circle_diameter = min(self.width(), self.height())
        circle_rect = QRect(self.rect().center().x() - circle_diameter / 2,
                            self.rect().center().y() - circle_diameter / 2,
                            circle_diameter, circle_diameter)
        circle_rect.adjust(self.circle_width, self.circle_width, -self.circle_width, -self.circle_width)

        square_width = math.sqrt(2) / 2 * circle_rect.width()
        square_rect = QRect(circle_rect.center().x() - square_width / 2,
                            circle_rect.center().y() - square_width / 2,
                            square_width, square_width)
        square_rect.adjust(2, 2, -2, -2)

        s_value = min((click_pos.x() - square_rect.x()) / square_rect.width() * 255, 255)
        v_value = min((square_rect.bottom() - click_pos.y()) / square_rect.height() * 255, 255)
        s_value = max(s_value, 0)
        v_value = max(v_value, 0)

        h, s, v = self.current_color.getHsv()
        current_color.setHsv(h, s_value, v_value)

    def Draw_wheel(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        circle_diameter = min(self.width(), self.height())
        circle_rect = QRect(self.rect().center().x() - circle_diameter / 2,
                            self.rect().center().y() - circle_diameter / 2,
                            circle_diameter, circle_diameter)

        # 设置圆环渐变颜色
        circle_gradient = QConicalGradient(self.rect().center(), 0)
        gap = 1 / len(self.circle_color_list)
        for i in range(len(self.circle_color_list)):
            circle_gradient.setColorAt(gap * i, self.circle_color_list[i])
        circle_gradient.setColorAt(1, self.circle_color_list[0])

        # 绘制圆环
        painter.setBrush(circle_gradient)
        painter.setPen(QPen(Qt.NoPen))
        painter.drawEllipse(circle_rect)

        # 绘制圆环中间部分
        circle_rect.adjust(self.circle_width, self.circle_width, -self.circle_width, -self.circle_width)
        painter.setBrush(self.style_manage_controller.background_color)
        painter.drawEllipse(circle_rect)

        # 绘制H选择圆圈
        h, s, v = self.current_color.getHsv()
        choose_ring_color = QColor()
        choose_ring_color.setHsv((h + 180) % 360, 255, 255)
        choose_ring_pen = QPen()
        choose_ring_pen.setColor(choose_ring_color)
        choose_ring_pen.setWidth(2)
        painter.setPen(choose_ring_pen)
        painter.setBrush(Qt.NoBrush)

        ring_pos = QVector2D(math.cos(h / (180 / 3.1415926)),
                             math.sin(h / (180 / 3.1415926)))
        ring_pos.normalize()
        ring_pos *= circle_rect.width() / 2 + self.circle_width / 2
        ring_pos = QVector2D(self.rect().center().x() + ring_pos.x(),
                             self.rect().center().y() - ring_pos.y())
        painter.drawEllipse(QPoint(ring_pos.x(), ring_pos.y()), self.circle_width / 3, self.circle_width / 3)

    def Draw_center_rect(self):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制正方形
        circle_diameter = min(self.width(), self.height())
        circle_rect = QRect(self.rect().center().x() - circle_diameter / 2,
                            self.rect().center().y() - circle_diameter / 2,
                            circle_diameter, circle_diameter)
        circle_rect.adjust(self.circle_width, self.circle_width, -self.circle_width, -self.circle_width)

        square_width = math.sqrt(2) / 2 * circle_rect.width()
        square_rect = QRect(circle_rect.center().x() - square_width / 2,
                            circle_rect.center().y() - square_width / 2,
                            square_width, square_width)
        square_rect.adjust(2, 2, -2, -2)

        # 绘制渐变
        h, s, v = self.current_color.getHsv()
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
        choose_ring_color = QColor()
        choose_ring_color.setHsv((h + 180) % 360, 255 - s, 255 - v)
        choose_ring_pen = QPen()
        choose_ring_pen.setColor(choose_ring_color)
        choose_ring_pen.setWidth(2)

        choose_ring_x = square_rect.width() * (s / 255)
        choose_ring_y = square_rect.height() * (v / 255)
        choose_ring_pos = QPoint(square_rect.bottomLeft().x() + choose_ring_x,
                                 square_rect.bottomLeft().y() - choose_ring_y)
        painter.setPen(choose_ring_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(choose_ring_pos, self.circle_width / 3, self.circle_width / 3)

    def paintEvent(self):
        self.Draw_wheel()
        self.Draw_center_rect()

    def resizeEvent(self, event):
        width = min(self.size().width(), self.size().height())
        self.circle_width = width / 8

        return super().resizeEvent(event)

    def mousePressEvent(self, event):
        self.select_mode_enum = 'normal'
        click_pos = event.pos()

        circle_diameter = min(self.width(), self.height())
        circle_rect = QRect(self.rect().center().x() - circle_diameter / 2,
                            self.rect().center().y() - circle_diameter / 2,
                            circle_diameter, circle_diameter)

        # 判断是否选中圆环
        pos_to_center_len = self.distance(self.rect().center(), click_pos)
        circle_outer_radius = abs(circle_rect.topLeft().x() - self.rect().center().x())
        circle_rect.adjust(self.circle_width, self.circle_width, -self.circle_width, -self.circle_width)
        circle_inner_radius = abs(circle_rect.topLeft().x() - self.rect().center().x())
        if circle_inner_radius < pos_to_center_len and pos_to_center_len < circle_outer_radius:
            self.select_mode_enum = 'circle'

        # 判断是否选中中间矩形
        square_width = math.sqrt(2) * circle_rect.width() / 2
        square_rect = QRect(circle_rect.center().x() - square_width / 2,
                            circle_rect.center().y() - square_width / 2,
                            square_width, square_width)
        square_rect.adjust(2, 2, -2, -2)
        if square_rect.contains(click_pos):
            self.select_mode_enum = 'rect'

        if self.select_mode_enum == 'circle':
            self.Update_h(click_pos)
            self.parent_widget.color_wheel_change_single.emit()
            self.update()
        elif self.select_mode_enum == 'rect':
            self.Update_s_and_v(click_pos)
            self.parent_widget.color_wheel_change_single.emit()
            self.update()

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        click_pos = event.pos()
        if self.select_mode_enum == 'circle':
            self.Update_h(click_pos)
            self.parent_widget.color_wheel_change_single.emit()
            self.update()
        elif self.select_mode_enum == 'rect':
            self.Update_s_and_v(click_pos)
            self.parent_widget.color_wheel_change_single.emit()
            self.update()

        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        click_pos = event.pos()
        if self.select_mode_enum == 'circle':
            self.Update_h(click_pos)
            self.parent_widget.color_wheel_change_single.emit()
            self.update()
        elif self.select_mode_enum == 'rect':
            self.Update_s_and_v(click_pos)
            self.parent_widget.color_wheel_change_single.emit()
            self.update()

        self.select_mode_enum = 'Normal'
        return super().mouseReleaseEvent(event)