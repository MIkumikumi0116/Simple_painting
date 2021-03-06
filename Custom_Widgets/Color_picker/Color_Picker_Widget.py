from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal

from .Color_Picker_Widget_UI import Ui_Color_Picker_Widget_UI



class Color_Picker_Widget(QWidget, Ui_Color_Picker_Widget_UI):
    color_change_singal = pyqtSignal(QColor)

    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.setupUi(self)
        self.style_manage_controller = [widget.Get_style_manage_controller()
                                        for widget in QApplication.topLevelWidgets()
                                        if 'Main_Window' in str(type(widget))][0]

        self.current_color = QColor(0,0,0)

        self.show_color_wheel_flag = True
        self.show_rgb_flag = True
        self.show_hsv_flag = True

        self.Color_Wheel_Widget.Set_current_color(self.current_color)

        self.R_Slider.Set_slider_type_enum('r_slider')
        self.R_Slider.Set_start_color(QColor(0, 0, 0))
        self.R_Slider.Set_end_color(QColor(255, 0, 0))

        self.G_Slider.Set_slider_type_enum('g_slider')
        self.G_Slider.Set_start_color(QColor(0, 0, 0))
        self.G_Slider.Set_end_color(QColor(0, 255, 0))

        self.B_Slider.Set_slider_type_enum('b_slider')
        self.B_Slider.Set_start_color(QColor(0, 0, 0))
        self.B_Slider.Set_end_color(QColor(0, 0, 255))

        self.H_Slider.Set_slider_type_enum('h_slider')

        self.S_Slider.Set_slider_type_enum('s_slider')
        self.S_Slider.Set_start_color(QColor(0, 0, 0))
        self.S_Slider.Set_end_color(QColor(0, 0, 0))

        self.V_Slider.Set_slider_type_enum('v_slider')
        self.V_Slider.Set_start_color(QColor(0, 0, 0))
        self.V_Slider.Set_end_color(QColor(255, 255, 255))

        self.Color_Wheel_Button.clicked.connect(self.On_color_wheel_button_clicked)
        self.RGB_Button.clicked.connect(self.On_rgb_button_clicked)
        self.HSV_Button.clicked.connect(self.On_hsv_button_clicked)

        self.Color_Wheel_Widget.color_wheel_change_single.connect(self.On_color_wheel_change_single_emit)

        self.R_LineEdit.textEdited.connect(self.On_r_lineedit_textedited)
        self.G_LineEdit.textEdited.connect(self.On_g_lineedit_textedited)
        self.B_LineEdit.textEdited.connect(self.On_b_lineedit_textedited)
        self.H_LineEdit.textEdited.connect(self.On_h_lineedit_textedited)
        self.S_LineEdit.textEdited.connect(self.On_s_lineedit_textedited)
        self.V_LineEdit.textEdited.connect(self.On_v_lineedit_textedited)

        self.R_Slider.color_slider_change_singal.connect(self.On_color_slider_change_singal_emit)
        self.G_Slider.color_slider_change_singal.connect(self.On_color_slider_change_singal_emit)
        self.B_Slider.color_slider_change_singal.connect(self.On_color_slider_change_singal_emit)
        self.H_Slider.color_slider_change_singal.connect(self.On_color_slider_change_singal_emit)
        self.S_Slider.color_slider_change_singal.connect(self.On_color_slider_change_singal_emit)
        self.V_Slider.color_slider_change_singal.connect(self.On_color_slider_change_singal_emit)


    def Update_color_wheel(self):
        self.Color_Wheel_Widget.Set_current_color(self.current_color)

    def Update_lineedit(self):
        r, g, b, _ = self.current_color.getRgb()
        h, s, v, _ = self.current_color.getHsv()
        h = max(0, h)

        self.R_LineEdit.setText(str(r))
        self.G_LineEdit.setText(str(g))
        self.B_LineEdit.setText(str(b))
        self.H_LineEdit.setText(str(h))
        self.S_LineEdit.setText(str(s))
        self.V_LineEdit.setText(str(v))

    def Update_slider(self):
        r, g, b, _ = self.current_color.getRgb()
        h, s, v, _ = self.current_color.getHsv()

        self.R_Slider.Set_start_color(QColor(0, g, b))
        self.R_Slider.Set_end_color(QColor(255, g, b))
        self.R_Slider.Set_current_value(r)

        self.G_Slider.Set_start_color(QColor(r, 0, b))
        self.G_Slider.Set_end_color(QColor(r, 255, b))
        self.G_Slider.Set_current_value(g)

        self.B_Slider.Set_start_color(QColor(r, g, 0))
        self.B_Slider.Set_end_color(QColor(r, g, 255))
        self.B_Slider.Set_current_value(b)

        self.H_Slider.Set_current_value(h)

        s_color = QColor()
        s_color.setHsv(h, 0, v)
        self.S_Slider.Set_start_color(s_color)
        s_color.setHsv(h, 255, v)
        self.S_Slider.Set_end_color(s_color)
        self.S_Slider.Set_current_value(s)

        v_color = QColor()
        v_color.setHsv(h, s, 0)
        self.V_Slider.Set_start_color(v_color)
        v_color.setHsv(h, s, 255)
        self.V_Slider.Set_end_color(v_color)
        self.V_Slider.Set_current_value(v)

    def Update_color(self):
        self.color_change_singal.emit(self.current_color)

        self.Update_color_wheel()
        self.Update_lineedit()
        self.Update_slider()


    def Get_current_color(self):
        return self.current_color

    def Set_current_color(self, color):
        r, g, b, _ = color.getRgb()
        self.current_color = QColor(r, g, b)

        self.Update_color_wheel()
        self.Update_lineedit()
        self.Update_slider()


    def On_color_wheel_button_clicked(self):
        if self.show_color_wheel_flag:
            self.Color_Wheel_Widget.setVisible(False)
            self.show_color_wheel_flag = False
        else:
            self.Color_Wheel_Widget.setVisible(True)
            self.show_color_wheel_flag = True

    def On_rgb_button_clicked(self):
        if self.show_rgb_flag:
            self.RGB_Layout.setVisible(False)
            self.show_rgb_flag = False
        else:
            self.RGB_Layout.setVisible(True)
            self.show_rgb_flag = True

    def On_hsv_button_clicked(self):
        if self.show_hsv_flag:
            self.HSV_Layout.setVisible(False)
            self.show_hsv_flag = False
        else:
            self.HSV_Layout.setVisible(True)
            self.show_hsv_flag = True


    def On_r_lineedit_textedited(self, text):
        if not text.isdigit():
            self.R_LineEdit.setText('0')
            value = 0
        else:
            if text.startswith('0'):
                text = text.lstrip('0')
                self.R_LineEdit.setText('0' if len(text) == 0 else text)
                value = 0 if len(text) == 0 else eval(text)
            else:
                value = eval(text)
                if value > 255:
                    self.R_LineEdit.setText('255')
                    value = 255

        r, g, b, _ = self.current_color.getRgb()
        self.current_color.setRgb(value, g, b)

        self.Update_color()

    def On_g_lineedit_textedited(self, text):
        if not text.isdigit():
            self.G_LineEdit.setText('0')
            value = 0
        else:
            if text.startswith('0'):
                text = text.lstrip('0')
                self.G_LineEdit.setText('0' if len(text) == 0 else text)
                value = 0 if len(text) == 0 else eval(text)
            else:
                value = eval(text)
                if value > 255:
                    self.G_LineEdit.setText('255')
                    value = 255

        r, g, b, _ = self.current_color.getRgb()
        self.current_color.setRgb(r, value, b)

        self.Update_color()

    def On_b_lineedit_textedited(self, text):
        if not text.isdigit():
            self.B_LineEdit.setText('0')
            value = 0
        else:
            if text.startswith('0'):
                text = text.lstrip('0')
                self.B_LineEdit.setText('0' if len(text) == 0 else text)
                value = 0 if len(text) == 0 else eval(text)
            else:
                value = eval(text)
                if value > 255:
                    self.B_LineEdit.setText('255')
                    value = 255

        r, g, b, _ = self.current_color.getRgb()
        self.current_color.setRgb(r, g, value)

        self.Update_color()

    def On_h_lineedit_textedited(self, text):
        if not text.isdigit():
            self.H_LineEdit.setText('0')
            value = 0
        else:
            if text.startswith('0'):
                text = text.lstrip('0')
                self.H_LineEdit.setText('0' if len(text) == 0 else text)
                value = 0 if len(text) == 0 else eval(text)
            else:
                value = eval(text)
                if value > 359:
                    self.H_LineEdit.setText('359')
                    value = 359

        h, s, v, _ = self.current_color.getHsv()
        self.current_color.setHsv(value, s, v)

        self.Update_color()

    def On_s_lineedit_textedited(self, text):
        if not text.isdigit():
            self.S_LineEdit.setText('0')
            value = 0
        else:
            if text.startswith('0'):
                text = text.lstrip('0')
                self.S_LineEdit.setText('0' if len(text) == 0 else text)
                value = 0 if len(text) == 0 else eval(text)
            else:
                value = eval(text)
                if value > 255:
                    self.S_LineEdit.setText('255')
                    value = 255

        h, s, v, _ = self.current_color.getHsv()
        self.current_color.setHsv(h, value, v)

        self.Update_color()

    def On_v_lineedit_textedited(self, text):
        if not text.isdigit():
            self.V_LineEdit.setText('0')
            value = 0
        else:
            if text.startswith('0'):
                text = text.lstrip('0')
                self.V_LineEdit.setText('0' if len(text) == 0 else text)
                value = 0 if len(text) == 0 else eval(text)
            else:
                value = eval(text)
                if value > 255:
                    self.V_LineEdit.setText('255')
                    value = 255

        h, s, v, _ = self.current_color.getHsv()
        self.current_color.setHsv(h, s, value)

        self.Update_color()


    def On_color_wheel_change_single_emit(self, color):
        h, s, v, _ = color.getHsv()
        self.current_color.setHsv(h, s, v)

        self.Update_color()

    def On_color_slider_change_singal_emit(self, slider_type_enum, value):
        if slider_type_enum == 'r_slider':
            r, g, b, _ = self.current_color.getRgb()
            self.current_color.setRgb(value, g, b)
        elif slider_type_enum == 'g_slider':
            r, g, b, _ = self.current_color.getRgb()
            self.current_color.setRgb(r, value, b)
        elif slider_type_enum == 'b_slider':
            r, g, b, _ = self.current_color.getRgb()
            self.current_color.setRgb(r, g, value)
        elif slider_type_enum == 'h_slider':
            h, s, v, _ = self.current_color.getHsv()
            self.current_color.setHsv(value, s, v)
        elif slider_type_enum == 's_slider':
            h, s, v, _ = self.current_color.getHsv()
            self.current_color.setHsv(h, value, v)
        elif slider_type_enum == 'v_slider':
            h, s, v, _ = self.current_color.getHsv()
            self.current_color.setHsv(h, s, value)

        self.Update_color()
