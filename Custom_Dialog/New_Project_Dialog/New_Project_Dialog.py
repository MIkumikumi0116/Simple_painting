import re

from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import sip

from .New_Project_Dialog_UI import Ui_New_Project_Dialog_UI



class New_Project_Dialog(QDialog, Ui_New_Project_Dialog_UI):
    def __init__(self, parent_window, callback_func):
        super().__init__(parent_window)
        self.setupUi(self)
        self.show()

        self.callback_func = callback_func

        self.Preset_Size_ComboBox.currentTextChanged.connect(self.On_preset_size_comboBox_text_changed)
        self.Width_LineEdit.textChanged.             connect(self.On_width_lineedit_text_changed)
        self.Height_LineEdit.textChanged.            connect(self.On_height_lineedit_text_changed)
        self.Confirm_Button.clicked.                 connect(self.On_confirm_button_clicked)
        self.Cancel_Button.clicked.                  connect(self.On_cancel_button_clicked)

    def On_preset_size_comboBox_text_changed(self, text):
        board_size = re.findall('(\d+)×(\d+)' ,text)[0]

        self.Width_LineEdit. setText(board_size[0])
        self.Height_LineEdit.setText(board_size[1])

    def On_width_lineedit_text_changed(self, text):
        if text == '':
            pass
        elif  not text.isdigit():
            self.Width_LineEdit.setText('256')
        else:
            if text.startswith('0'):
                text = text.lstrip('0')
                self.Width_LineEdit.setText('' if len(text) == 0 else text)
            else:
                if eval(text) > 100000:
                    self.Width_LineEdit.setText('100000')
                elif eval(text) <= 0:
                    self.Width_LineEdit.setText('1')

    def On_height_lineedit_text_changed(self, text):
        if text == '':
            pass
        elif  not text.isdigit():
            self.Height_LineEdit.setText('256')
        else:
            if text.startswith('0'):
                text = text.lstrip('0')
                self.Height_LineEdit.setText('' if len(text) == 0 else text)
            else:
                if eval(text) > 100000:
                    self.Height_LineEdit.setText('100000')
                elif eval(text) <= 0:
                    self.Height_LineEdit.setText('1')

    def On_confirm_button_clicked(self):
        if self.Width_LineEdit.text() == '' or self.Height_LineEdit.text() == '':
            QMessageBox.information(self, '错误', '请输入画布大小', QMessageBox.Yes, QMessageBox.Yes)
            return

        board_size = (eval(self.Width_LineEdit.text()), eval(self.Height_LineEdit.text()))
        self.callback_func(board_size)
        self.close()
        sip.delete(self)

    def On_cancel_button_clicked(self):
        self.close()
