from PyQt5.QtWidgets import QWidget, QApplication

from .Layer_Widget_UI import Ui_Layer_Widget_UI



class Layer_Widget(QWidget,Ui_Layer_Widget_UI):
    def __init__(self,parent_widget):
        super().__init__(parent_widget)
        self.setupUi(self)

        self.style_manage_controller = [widget.Get_style_manage_controller()
                                        for widget in QApplication.topLevelWidgets()
                                        if 'Main_Window' in str(type(widget))][0]