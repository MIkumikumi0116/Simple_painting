from PIL import ImageQt

from PyQt5.QtWidgets import QWidget, QApplication

from .Layer_Widget_UI import Ui_Layer_Widget_UI



class Layer_Widget(QWidget,Ui_Layer_Widget_UI):
    def __init__(self,parent_widget):
        super().__init__(parent_widget)
        self.setupUi(self)

        self.layer = None

        self.style_manage_controller = [widget.Get_style_manage_controller()
                                        for widget in QApplication.topLevelWidgets()
                                        if 'Main_Window' in str(type(widget))][0]

    def init(self, layer):
        self.layer = layer

    def Get_preview_label_size(self):
        size = self.Preview_Label.size()
        return (size.width(), size.height())

    def Set_preview_label(self, image):
        self.Preview_Label.setPixmap(ImageQt.toqpixmap(image))

    def Set_widget_info(self):
        self.Name_Label.setText(self.layer.name)
        self.Mod_Label.setText(self.layer.mod_enum)
        self.Opacity_Label.setText(f'{self.layer.opacity}%')

        self.Hide_Button.setChecked(self.layer.hide_flag)
        self.Lock_Button.setChecked(self.layer.lock_flag)