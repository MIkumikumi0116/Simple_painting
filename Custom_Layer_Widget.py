from PyQt5 import QtWidgets

from Custom_Layer_Widget_UI import Ui_Custom_Layer_Widget_UI


class Custom_Layer_Widget(QtWidgets.QWidget,Ui_Custom_Layer_Widget_UI):
    def __init__(self,parent_widget):
        super().__init__()
        self.setParent(parent_widget)
        self.setupUi(self)