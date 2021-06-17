from PyQt5.QtWidgets import QWidget

from .Layer_Widget_UI import Ui_Layer_Widget_UI



class Layer_Widget(QWidget,Ui_Layer_Widget_UI):
    def __init__(self,parent_widget):
        super().__init__(parent_widget)
        self.setupUi(self)