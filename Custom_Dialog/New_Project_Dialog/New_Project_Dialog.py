from PyQt5.QtWidgets import QDialog

from .New_Project_Dialog_UI import Ui_New_Project_Dialog_UI


class New_Project_Dialog(QDialog, Ui_New_Project_Dialog_UI):
    def __init__(self, parent_window, callback_func):
        super().__init__(parent_window)
        self.setupUi()

        self.callback_func = callback_func
