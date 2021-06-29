from PIL import ImageQt

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QPalette
from PyQt5.QtCore import pyqtSignal

from .Layer_Widget_UI import Ui_Layer_Widget_UI



class Layer_Widget(QWidget,Ui_Layer_Widget_UI):
    mouse_press_singal = pyqtSignal()

    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.setupUi(self)
        self.setAutoFillBackground(True)

        self.layer = None
        self.style_manage_controller = None

    def init(self, layer, style_manage_controller):
        self.layer = layer
        self.style_manage_controller = style_manage_controller

    def Get_preview_label_size(self):
        return (self.Preview_Label.size().width(), self.Preview_Label.size().height())

    def Set_preview_label(self, image):
        self.Preview_Label.setPixmap(ImageQt.toqpixmap(image))

    def Set_widget_info(self):
        self.Name_Label.setText(self.layer.name)
        self.Mod_Label.setText(self.layer.mod_enum)
        self.Opacity_Label.setText(f'{self.layer.opacity}%')

        self.Hide_Button.setChecked(self.layer.hide_flag)
        self.Lock_Button.setChecked(self.layer.lock_flag)

        palette = self.palette()
        state_enum = self.layer.selected_state_enum

        if state_enum == 'unselected':
            palette.setColor(QPalette.Background, self.style_manage_controller.Get_highlight_front_color())
        elif state_enum == 'strong_selected':
            palette.setColor(QPalette.Background, self.style_manage_controller.Get_strong_selected_color())
        elif state_enum == 'weak_selected':
            palette.setColor(QPalette.Background, self.style_manage_controller.Get_weak_selected_color())

        self.setPalette(palette)

    def mousePressEvent(self, event):
        self.mouse_press_singal.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(self.style_manage_controller.Get_board_color())
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(self.rect())

        super().paintEvent(event)