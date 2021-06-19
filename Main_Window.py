import sys
import numpy as np
from PIL import Image, ImageQt

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QColor
from PyQt5.QtCore import QTimer

from Main_Window_UI import Ui_Main_Window_UI



class Frame_View:
    def __init__(self, main_window):
        self.main_window = main_window

    def init(self):
        pass


class Frame_Controller:
    class Frame:
        def __init__(self, controller):
            self.controller = controller

            self.layer_list = []

        def Insert_layer(self, layer, index = None):
            if index == None:
                self.layer_list.append(layer)
            else:
                self.layer_list.inset(index, layer)

    def __init__(self, main_window):
        self.main_window = main_window

        self.frame_list = [Frame_Controller.Frame(self)]
        self.current_frame = self.frame_list[0]

    def init(self):
        self.current_frame.Insert_layer(self.board_layer_controller.Yield_blank_layer())

    def Get_current_frame(self):
        return self.current_frame


class Board_Layer_View:
    def __init__(self, main_window):
        self.main_window = main_window

        self.board_background_image = None

    def init(self):
        r, g, b, _ = self.style_manage_controller.Get_base_color().getRgb()
        self.board_background_image = Image.new('RGBA',
                                                (self.main_window.Board_Label.width(), self.main_window.Board_Label.height()),
                                                (r, g, b))

    def _Init_print(self, image):
        board_size = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())
        image_size = image.size
        zoom_time = self.board_layer_controller.Get_zoom_time()


        if image_size[0] < board_size[0] and image_size[1] < board_size[1]:
            narrow_type = 'no_narrow'
        elif image_size[0] > board_size[0] and image_size[1] < board_size[1]:
            narrow_type = 'h_narrow'
        elif image_size[0] < board_size[0] and image_size[1] > board_size[1]:
            narrow_type = 'v_narrow'
        else:
            if image_size[0] / board_size[0] > image_size[1] / board_size[1]:
                narrow_type = 'h_narrow'
            else:
                narrow_type = 'v_narrow'

        if narrow_type == 'no_narrow':
            if image_size[0] / board_size[0] > image_size[1] / board_size[1]:
                zoom_time = board_size[0] // image_size[0]
            else:
                zoom_time = board_size[1] // image_size[1]
            image = image.resize((image_size[0] * zoom_time, image_size[1] * zoom_time), Image.NEAREST)

        elif narrow_type == 'h_narrow':
            zoom_time = -(image_size[0] // board_size[0] + 1)
            image = image.resize((image_size[0] // -zoom_time, image_size[1] // -zoom_time), Image.NEAREST)

        elif narrow_type == 'v_narrow':
            zoom_time = -(image_size[1] // board_size[1] + 1)
            image = image.resize((image_size[0] // -zoom_time, image_size[1] // -zoom_time), Image.NEAREST)

        board_image = self.board_background_image.copy()
        board_image.paste(image, ((board_image.size[0] - image.size[0]) // 2,(board_image.size[1] - image.size[1]) // 2))
        self.main_window.Board_Label.setPixmap(ImageQt.toqpixmap(board_image))

    def Print_image(self, image):
        image_size = image.size
        zoom_time = self.board_layer_controller.Get_zoom_time()

        if zoom_time > 0:
            image = image.resize((image_size[0] * zoom_time, image_size[1] * zoom_time), Image.NEAREST)
        else:
            image = image.resize((image_size[0] / -zoom_time, image_size[1] / -zoom_time), Image.NEAREST)

        board_image = self.board_background_image.copy()
        board_image.paste(image, ((board_image.size[0] - image.size[0]) // 2,(board_image.size[1] - image.size[1]) // 2))
        self.main_window.Board_Label.setPixmap(ImageQt.toqpixmap(board_image))


class Board_Layer_Controller:
    class Layer:
        def __init__(self, controller, image = None, offset = (0, 0), angle = 0):
            self.controller = controller
            self.image = image if image != None else Image.new('RGBA', self.controller.Get_board_size(), (255, 255, 255))
            self.offset = offset
            self.angle = angle

        def Get_size(self):
            return self.image.size

    def __init__(self, main_window):
        self.main_window = main_window

        self.board_size = (256, 256)
        self.board_offset = (0, 0)
        self.h_scrollbar_enabled = False
        self.v_scrollbar_enabled = False
        self.zoom_time = 1
        self.current_frame = None
        self.layer_list = None
        self.selected_layer_list = None
        self.background_layer = Image.new('RGBA', self.board_size, (255, 255, 255))

    def init(self):
        self.current_frame = self.frame_controller.Get_current_frame()
        self.layer_list = self.current_frame.layer_list
        self.selected_layer_list = [self.layer_list[0]]

        painting = self.background_layer.copy()
        for layer in self.layer_list:
            painting.paste(layer.image, layer.offset)

        self.board_layer_view._Init_print(painting)

    def Draw_painting(self):
        painting = self.background_layer.copy()
        for layer in self.layer_list:
            painting.paste(layer, layer.offset)

        self.board_layer_view.Print_image(painting)

    def Yield_blank_layer(self):
        return Board_Layer_Controller.Layer(self)

    def Get_zoom_time(self):
        return self.zoom_time

    def Set_zoom_time(self, value):
        self.zoom_time = value

    def Get_board_size(self):
        return self.board_size

    def Set_board_size(self, board_size):
        self.board_size = board_size

    def Get_selected_layer(self):
        if len(self.selected_layer_list) == 1:
            return self.selected_layer_list[0]
        else:
            return False

    def Get_selected_layer_list(self):
        return self.selected_layer_list


class Color_View:
    def __init__(self, main_window):
        self.main_window = main_window

    def init(self):
        pass


class Color_Controller:
    def __init__(self, main_window):
        self.main_window = main_window

        self.front_color = (0, 0, 0)
        self.back_color = (255, 255, 255)

    def init(self):
        pass

    def Get_front_color(self):
        return self.front_color


class Tool_View:
    def __init__(self, main_window):
        self.main_window = main_window

    def init(self):
        pass


class Tool_Controller:
    class Pencil_Tool:
        def __init__(self, controller):
            self.controller = controller

            self.brush_size = 10

        def Mouse_press_event(self, x, y):
            layer = self.controller._Get_selected_layer()
            if layer == False:
                self.controller._Send_label_notify('该工具只能作用于单个图层')
                return

            self.controller._Declare_image_edited()

            radius = self.brush_size // 2
            board_size = self.controller._Get_board_size()
            pixel_matrix_np = np.array(layer.image, dtype='int')
            color =  np.array(self.controller._Get_front_color())

            paint_area = [(i, j) for i in range(x - radius, x + radius + 1)
                                 for j in range(y - radius, y + radius + 1)
                                 if abs((i - x)) ** 2 + abs((j - y)) ** 2 <= radius ** 2
                                 and 0 <= i and i < board_size[0]
                                 and 0 <= j and j < board_size[1]]

            for point in paint_area:
                pixel_matrix_np[point[1], point[0]] = color

            layer.image = Image.fromarray(pixel_matrix_np)

            self.controller._Draw_painting()

    def __init__(self, main_window):
        self.main_window = main_window

        self.current_tool = None

        self.pencil_tool = Tool_Controller.Pencil_Tool(self)

    def init(self):
        self.current_tool = self.pencil_tool

    def _Get_selected_layer(self):
        return self.board_layer_controller.Get_selected_layer()

    def _Send_label_notify(self, text):
        self.notify_controller.Label_notify(text)

    def _Declare_image_edited(self):
        self.main_window.Declare_image_edited()

    def _Get_board_size(self):
        return self.board_layer_controller.Get_board_size()

    def _Get_front_color(self):
        return self.color_controller.Get_front_color()

    def _Get_zoom_time(self):
        return self.board_layer_controller.Get_zoom_time()

    def _Draw_painting(self):
        self.board_layer_controller.Draw_painting()

    def Mouse_press_event(self, event):
        x, y = event.pos()
        zoom_time = self._Get_zoom_time()
        board_size = self.board_layer_controller.Get_board_size()

        self.current_tool.Mouse_press_event(x, y)

    def Mouse_move_event(self, event):
        self.current_tool.Mouse_move_event(event)

    def Mouse_release_event(self, event):
        self.current_tool.Mouse_release_event(event)


class Notify_Controller:
    def __init__(self, main_window):
        self.main_window = main_window

        self.label_notify_timer = QTimer()
        self.label_notify_timer.timeout.connect(self.On_label_notify_time_out)

    def init(self):
        pass

    def Label_notify(self, text):
        self.main_window.Notify_Label.setText(text)
        self.label_notify_timer.start(3000)

    def On_label_notify_time_out(self):
        self.main_window.Notify_Label.setText('')


class Backup_Controller:
    def __init__(self, main_window):
        self.main_window = main_window

    def init(self):
        pass


class Style_Manage_Controller:
    def __init__(self, main_window):
        self.main_window = main_window

        self.base_color = QColor(240, 240, 240)
        self.board_color = QColor(160 ,160, 160)
        self.text_color = QColor(0, 0, 0)

    def init(self):
        pass

    def Get_base_color(self):
        return self.base_color

    def Get_board_color(self):
        return self.board_color

    def Get_text_color(self):
        return self.text_color


class Event_And_Singal_Distributor:
    def __init__(self, main_window):
        self.main_window = main_window

    def init(self):
        self.main_window.Board_Label.mousePressEvent = self.tool_controller.Mouse_press_event
        self.main_window.Board_Label.mouseMoveEvent = self.tool_controller.Mouse_move_event
        self.main_window.Board_Label.mouseReleaseEvent = self.tool_controller.Mouse_release_event


class Main_Window(QMainWindow, Ui_Main_Window_UI):
    def __init__(self):
        super().__init__()

        self.main_window = self

        self.frame_view = Frame_View(self.main_window)
        self.frame_controller = Frame_Controller(self.main_window)
        self.board_layer_view = Board_Layer_View(self.main_window)
        self.board_layer_controller = Board_Layer_Controller(self.main_window)
        self.color_view = Color_View(self.main_window)
        self.color_controller = Color_Controller(self.main_window)
        self.tool_view = Tool_View(self.main_window)
        self.tool_controller = Tool_Controller(self.main_window)
        self.notify_controller = Notify_Controller(self.main_window)
        self.backup_controller = Backup_Controller(self.main_window)
        self.style_manage_controller = Style_Manage_Controller(self.main_window)
        self.event_and_singal_distributor = Event_And_Singal_Distributor(self.main_window)

        self.setupUi(self)
        self.main_window.show()
        self.Init_ui_and_module()

        self.image_edited_flag = False

        self.module_list = [self.frame_view,
                            self.frame_controller,
                            self.board_layer_view,
                            self.board_layer_controller,
                            self.color_view,
                            self.color_controller,
                            self.tool_view,
                            self.tool_controller,
                            self.notify_controller,
                            self.backup_controller,
                            self.style_manage_controller,
                            self.event_and_singal_distributor]

        for module in self.module_list:
            module.frame_view = self.frame_view
            module.frame_controller = self.frame_controller
            module.board_layer_view = self.board_layer_view
            module.board_layer_controller = self.board_layer_controller
            module.tool_view = self.tool_view
            module.tool_controller = self.tool_controller
            module.notify_controller = self.notify_controller
            module.backup_controller = self.backup_controller
            module.style_manage_controller = self.style_manage_controller
            module.event_and_singal_distributor = self.event_and_singal_distributor

        for module in self.module_list:
            module.init()

    def Init_ui_and_module(self):
        # self.main_window.self.Color_Picker_Widget.
        self.main_window.Pencil_Size_ComboBox.setStyleSheet('''#Pencil_Size_ComboBox QAbstractItemView{min-width: 60px;}''')

    def Declare_image_edited(self):
        self.image_edited_flag = True

    def Get_style_manage_controller(self):
        return self.style_manage_controller



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Main_Window()
    sys.exit(app.exec_())