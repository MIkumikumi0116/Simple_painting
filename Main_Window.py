import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage

from Main_Window_UI import Ui_Main_Window_UI



class Paintint_Tool_Controller:
    class Pencil_Tool:
        def __init__(self):
            self.brush_size = 10

    def __init__(self, main_window):
        self.main_window = main_window

        self.pencil_tool = Pencil_Tool()



class Frame_Controller:
    class Frame:
        def __init__(self):
            self.layer_list = [Layer_Controller.Layer()]

    def __init__(self, main_window):
        self.main_window = main_window



class Layer_Controller:
    class Layer:
        def __init__(self):
            self.image = QImage()

    def __init__(self, main_window):
        self.main_window = main_window



class Board_Controller:
    def __init__(self, main_window):
        self.main_window = main_window



class Event_And_Singal_Distributor:
    def __init__(self, main_window):
        self.main_window = main_window



class Main_Window(QMainWindow, Ui_Main_Window_UI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.Init_ui_and_module()

        self.main_window = self
        self.Event_and_singal_Distributor = Event_And_Singal_Distributor(self.main_window)
        self.paintint_tool_controller = Paintint_Tool_Controller(self.main_window)
        self.board_controller = Board_Controller(self.main_window)

    def Link_module(self):
        module_list = [self.event_distributor]

        for module in module_list:
            module.event_distributor = self.Event_and_singal_Distributor
            module.paintint_tool_controller = self.paintint_tool_controller
            module.board_controller = self.board_controller

    def Init_ui_and_module(self):
        self.Pencil_Size_ComboBox.setStyleSheet('''#Pencil_Size_ComboBox QAbstractItemView{min-width: 60px;}''')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Main_Window()
    main_window.show()
    sys.exit(app.exec_())