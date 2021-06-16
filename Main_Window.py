import sys

from Main_Window_UI import Ui_Main_Window_UI

from PyQt5.QtWidgets import QApplication, QMainWindow



class Main_Window(QMainWindow, Ui_Main_Window_UI):
    def __init__(self):
        super().__init__()
        self.setupUi(self)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Main_Window()
    main_window.show()
    sys.exit(app.exec_())