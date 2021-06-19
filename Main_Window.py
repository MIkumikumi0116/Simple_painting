import sys
import math
import time
import numpy as np
from threading import Thread
from PIL import Image, ImageQt

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QColor
from PyQt5.QtCore import QTimer, QPoint

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
        self.current_frame.Insert_layer(self.board_layer_controller.Get_blank_layer())

    def Get_current_frame(self):
        return self.current_frame


class Board_Layer_View:
    def __init__(self, main_window):
        self.main_window = main_window

        self.camera_zoom = None
        self.camera_rotate = 0
        self.camera_offset = (0, 0)
        self.camera_board_size = (None ,None)
        self.h_scrollbar_flag = False
        self.v_scrollbar_flag = False

        self.label_background_image = None

    def init(self):
        pass

    def _Init_print(self, image):
        # init camera_zoom, camera_board_size, label_background_image
        image_size = image.size
        label_size = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())
        r, g, b, _ = self.style_manage_controller.Get_base_color().getRgb()
        self.label_background_image = Image.new('RGBA',
                                                (label_size[0], label_size[1]),
                                                (r, g, b))
        label_background_image = self.label_background_image.copy()

        if image_size[0] < label_size[0] and image_size[1] < label_size[1]:
            narrow_type = 'no_narrow'
        elif image_size[0] > label_size[0] and image_size[1] < label_size[1]:
            narrow_type = 'h_narrow'
        elif image_size[0] < label_size[0] and image_size[1] > label_size[1]:
            narrow_type = 'v_narrow'
        else:
            if image_size[0] / label_size[0] > image_size[1] / label_size[1]:
                narrow_type = 'h_narrow'
            else:
                narrow_type = 'v_narrow'

        if narrow_type == 'no_narrow':
            if image_size[0] / label_size[0] > image_size[1] / label_size[1]:
                camera_zoom = label_size[0] // image_size[0]
            else:
                camera_zoom = label_size[1] // image_size[1]
            image_transferred = image.resize((image_size[0] * camera_zoom, image_size[1] * camera_zoom), Image.NEAREST)

        elif narrow_type == 'h_narrow':
            camera_zoom = -(image_size[0] // label_size[0] + 1)
            image_transferred = image.resize((image_size[0] // -camera_zoom, image_size[1] // -camera_zoom), Image.NEAREST)

        elif narrow_type == 'v_narrow':
            camera_zoom = -(image_size[1] // label_size[1] + 1)
            image_transferred = image.resize((image_size[0] // -camera_zoom, image_size[1] // -camera_zoom), Image.NEAREST)

        self.camera_zoom = camera_zoom
        self.camera_board_size = image_transferred.size

        label_background_image.paste(image_transferred,
                        ((label_size[0] - image_transferred.size[0]) // 2,
                         (label_size[1] - image_transferred.size[1]) // 2))
        self.main_window.Board_Label.setPixmap(ImageQt.toqpixmap(label_background_image))

    def Print_image(self, image):
        camera_zoom = self.camera_zoom
        camera_rotate = self.camera_rotate
        camera_offset = self.camera_offset

        image_size = image.size
        label_size = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())
        r, g, b, _ = self.style_manage_controller.Get_base_color().getRgb()
        self.label_background_image = Image.new('RGBA',
                                                (label_size[0], label_size[1]),
                                                (r, g, b))
        label_background_image = self.label_background_image.copy()

        image = image.resize(((image_size[0] * camera_zoom) if camera_zoom > 0 else (image_size[0] // -camera_zoom),
                              (image_size[1] * camera_zoom) if camera_zoom > 0 else (image_size[1] // -camera_zoom)),
                               Image.NEAREST)
        image_transferred = image.rotate(-camera_rotate, resample = Image.NEAREST, fillcolor = (r, g, b))
        image_transferred_size = image_transferred.size
        self.camera_board_size = image_transferred_size

        drawn_image_rect = [0, 0, 0, 0]
        drawn_image_rect[0] = self.camera_offset[0] if self.h_scrollbar_flag else 0
        drawn_image_rect[1] = self.camera_offset[1] if self.v_scrollbar_flag else 0
        drawn_image_rect[2] = self.camera_offset[0] + label_size[0] if self.h_scrollbar_flag else image_transferred_size[0]
        drawn_image_rect[3] = self.camera_offset[1] + label_size[1] if self.v_scrollbar_flag else image_transferred_size[1]

        drawn_label_rect = [0, 0, 0, 0]
        drawn_label_rect[0] = 0 if self.h_scrollbar_flag else (label_size[0] - image_transferred_size[0]) // 2
        drawn_label_rect[1] = 0 if self.v_scrollbar_flag else (label_size[1] - image_transferred_size[1]) // 2
        drawn_label_rect[2] = label_size[0] if self.h_scrollbar_flag else drawn_label_rect[0] + image_transferred_size[0]
        drawn_label_rect[3] = label_size[1] if self.v_scrollbar_flag else drawn_label_rect[1] + image_transferred_size[1]

        drawn_image = image_transferred.crop(tuple(drawn_image_rect))
        label_background_image.paste(drawn_image, tuple(drawn_label_rect))
        self.main_window.Board_Label.setPixmap(ImageQt.toqpixmap(label_background_image))

    def Click_pos_to_board_pos(self, click_x, click_y):
        camera_zoom = self.camera_zoom
        camera_rotate = self.camera_rotate
        camera_offset = self.camera_offset
        camera_board_size = self.camera_board_size

        board_size = self.board_layer_controller.Get_board_size()
        label_size = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())

        board_x = (click_x + camera_offset[0]) if self.h_scrollbar_flag else (click_x - (label_size[0] - camera_board_size[0]) / 2)
        board_y = (click_y + camera_offset[1]) if self.v_scrollbar_flag else (click_y - (label_size[1] - camera_board_size[1]) / 2)

        board_vector  = np.array([board_x , board_y])
        board_vector -= np.array([camera_board_size[0] / 2, camera_board_size[1] / 2])

        angle = np.radians(camera_rotate)
        cos, sin = np.cos(angle), np.sin(angle)
        rotate_matrix = np.array([[ cos, sin],
                                  [-sin, cos]])
        scale_matrix  = np.array([[(1 / camera_zoom) if camera_zoom > 0 else -camera_zoom, 0],
                                  [0, (1 / camera_zoom) if camera_zoom > 0 else -camera_zoom]])

        board_vector = np.dot(rotate_matrix, board_vector)
        board_vector = np.dot(scale_matrix, board_vector)
        board_vector += np.array([board_size[0] / 2, board_size[1] / 2])

        return round(board_vector[0]), round(board_vector[1])

    def Mouse_press_event(self, event):
        click_x, click_y = event.pos().x(), event.pos().y()
        board_x, board_y = self.Click_pos_to_board_pos(click_x, click_y)
        board_size = self.board_layer_controller.Get_board_size()

        if 0 <= board_x < board_size[0] and 0 <= board_y < board_size[1]:
            self.tool_controller.Mouse_press_event(click_x, click_y, board_x, board_y)

    def Mouse_move_event(self, event):
        click_x, click_y = event.pos().x(), event.pos().y()
        board_x, board_y = self.Click_pos_to_board_pos(click_x, click_y)
        board_size = self.board_layer_controller.Get_board_size()

        if 0 <= board_x < board_size[0] and 0 <= board_y < board_size[1]:
            self.tool_controller.Mouse_move_event(click_x, click_y, board_x, board_y)

    def Mouse_release_event(self, event):
        click_x, click_y = event.pos().x(), event.pos().y()
        board_x, board_y = self.Click_pos_to_board_pos(click_x, click_y)
        board_size = self.board_layer_controller.Get_board_size()

        if 0 <= board_x < board_size[0] and 0 <= board_y < board_size[1]:
            self.tool_controller.Mouse_release_event(click_x, click_y, board_x, board_y)

    def Get_camera_zoom(self):
        return self.camera_zoom

    def Set_camera_zoom(self, value):
        self.camera_zoom = value

    def Get_camera_rotate(self):
        return self.camera_rotate

    def Set_camera_rotate(self, value):
        self.camera_rotate = value

    def Get_camera_offset(self):
        return self.camera_offset

    def Set_camera_offset(self, value):
        self.camera_offset = value

    def Get_camera_board_size(self):
        return self.camera_board_size

    def Set_camera_board_size(self, camera_board_size):
        self.camera_board_size = camera_board_size

    def Get_h_scrollbar_flag(self):
        return self.h_scrollbar_flag

    def Set_h_scrollbar_flag(self, flag):
        self.h_scrollbar_flag = flag

    def Get_v_scrollbar_flag(self):
        return self.v_scrollbar_flag

    def Set_v_scrollbar_flag(self, flag):
        self.v_scrollbar_flag = flag


class Board_Layer_Controller:
    class Layer:
        def __init__(self, controller, image = None, zoom = 1, rotate = 0, offset = (0, 0)):
            self.controller = controller
            self.image = image if image != None else Image.new('RGBA', self.controller.Get_board_size(), (255, 255, 255))
            self.zoom = zoom
            self.rotate = rotate
            self.offset = offset

        def Get_size(self):
            return self.image.size

    def __init__(self, main_window):
        self.main_window = main_window

        self.board_size = (256, 256)
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
            layer_image = layer.image.copy()
            layer_image_size = layer.Get_size()
            layer_image = layer_image.resize((layer_image_size[0] * layer.zoom,
                                              layer_image_size[1] * layer.zoom),
                                              Image.NEAREST)
            layer_image= layer_image.rotate(-layer.rotate, resample = Image.NEAREST, fillcolor = (0, 0, 0, 0))

            if layer.offset[0] < 0:
                layer_image = layer_image.crop((-layer.offset[0], 0, layer_image.size[0], layer_image.size[1]))
            if layer.offset[1] < 0:
                layer_image = layer_image.crop((0, -layer.offset[1], layer_image.size[0], layer_image.size[1]))
            if layer.offset[0] + layer_image.size[0] > self.board_size[0]:
                layer_image = layer_image.crop((0, 0, layer.offset[0] + layer_image.size[0] - self.board_size[0], layer_image.size[1]))
            if layer.offset[1] + layer_image.size[1] > self.board_size[1]:
                layer_image = layer_image.crop((0, 0, layer_image.size[0], layer.offset[1] + layer_image.size[1] - self.board_size[1]))

            painting.paste(layer.image,
                          (layer.offset[0] if layer.offset[0] >= 0 else 0,
                           layer.offset[1] if layer.offset[1] >= 0 else 0))

        self.board_layer_view._Init_print(painting)

    def Draw_painting(self):
        painting = self.background_layer.copy()
        for layer in self.layer_list:
            layer_image = layer.image.copy()
            layer_image_size = layer.Get_size()
            layer_image = layer_image.resize((layer_image_size[0] * layer.zoom,
                                              layer_image_size[1] * layer.zoom),
                                              Image.NEAREST)
            layer_image= layer_image.rotate(-layer.rotate, resample = Image.NEAREST, fillcolor = (0, 0, 0, 0))

            if layer.offset[0] < 0:
                layer_image = layer_image.crop(-layer.offset[0], 0, layer_image.size[0], layer_image.size[1])
            if layer.offset[1] < 0:
                layer_image = layer_image.crop(0, -layer.offset[1], layer_image.size[0], layer_image.size[1])
            if layer.offset[0] + layer_image.size[0] > self.board_size[0]:
                layer_image = layer_image.crop(0, 0, layer.offset[0] + layer_image.size[0] - self.board_size[0], layer_image.size[1])
            if layer.offset[1] + layer_image.size[1] > self.board_size[1]:
                layer_image = layer_image.crop(0, 0, layer_image.size[0], layer.offset[1] + layer_image.size[1] - self.board_size[1])

            painting.paste(layer.image,
                          (layer.offset[0] if layer.offset[0] >= 0 else 0,
                           layer.offset[1] if layer.offset[1] >= 0 else 0))

        self.board_layer_view.Print_image(painting)

    def Get_blank_layer(self):
        return Board_Layer_Controller.Layer(self)

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

        self.front_color = QColor(0, 0, 0)
        self.back_color  = QColor(255, 255, 255)

    def init(self):
        pass

    def Get_front_color(self):
        return self.front_color

    def Set_front_color(self, color):
        r, g, b, _ = color.getRgb()
        self.front_color.setRgb(r, g, b)

    def Get_back_color(self):
        return self.back_color

    def Set_back_color(self, color):
        r, g, b, _ = color.getRgb()
        self.back_color.setRgb(r, g, b)


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

        def Pencil_draw(self, x, y):
            layer = self.controller._Get_selected_layer()
            if layer == False:
                self.controller._Send_label_notify('该工具只能作用于单个图层')
                return

            self.controller._Set_image_edited()

            radius = self.brush_size // 2
            board_size = self.controller._Get_board_size()
            pixel_matrix_np = np.array(layer.image, dtype = 'uint8')
            r, g, b, _ = self.controller._Get_front_color().getRgb()
            color = np.array((r, g, b, 255))

            # TODO 插值
            paint_area = [(i, j) for i in range(x - radius, x + radius + 1)
                                 for j in range(y - radius, y + radius + 1)
                                 if abs(i - x) ** 2 + abs(j - y) ** 2 <= radius ** 2
                                 and 0 <= i < board_size[0]
                                 and 0 <= j < board_size[1]]

            for point in paint_area:
                pixel_matrix_np[point[1], point[0]] = color

            layer.image = Image.fromarray(pixel_matrix_np)

            self.controller._Draw_painting()

        def Mouse_press_event(self, x, y):
            self.Pencil_draw(x, y)

        def Mouse_move_event(self, x, y):
            self.Pencil_draw(x, y)

        def Mouse_release_event(self, x, y):
            self.Pencil_draw(x, y)

    def __init__(self, main_window):
        self.main_window = main_window

        self.current_tool = None

        self.pencil_tool = Tool_Controller.Pencil_Tool(self)

        self.board_pos_only_list = [self.pencil_tool]

    def init(self):
        self.current_tool = self.pencil_tool

    def Mouse_press_event(self, click_x, click_y, board_x, board_y):
        if self.current_tool in self.board_pos_only_list:
            self.current_tool.Mouse_press_event(board_x, board_y)

    def Mouse_move_event(self, click_x, click_y, board_x, board_y):
        if self.current_tool in self.board_pos_only_list:
            self.current_tool.Mouse_move_event(board_x, board_y)

    def Mouse_release_event(self, click_x, click_y, board_x, board_y):
        if self.current_tool in self.board_pos_only_list:
            self.current_tool.Mouse_release_event(board_x, board_y)

    def _Get_selected_layer(self):
        return self.board_layer_controller.Get_selected_layer()

    def _Send_label_notify(self, text):
        self.notify_controller.Label_notify(text)

    def _Set_image_edited(self):
        self.main_window.Set_image_edited()

    def _Get_board_size(self):
        return self.board_layer_controller.Get_board_size()

    def _Get_front_color(self):
        return self.color_controller.Get_front_color()

    def _Draw_painting(self):
        self.board_layer_controller.Draw_painting()


class Notify_Controller:
    def __init__(self, main_window):
        self.main_window = main_window

        self.label_notify_list = []
        self.label_notify_thread = Thread(target = self.Label_notify_thread_action, args = ())
        self.label_notify_busy_flag = False
        self.label_notify_timer = QTimer()
        self.label_notify_timer.timeout.connect(self.On_label_notify_timer_timeout)

    def init(self):
        pass

    def Label_notify_thread_action(self):
        while True:
            time.sleep(0.05)

            if len(self.label_notify_list) > 0 and not self.label_notify_busy_flag:
                label_notify = self.label_notify_list.pop(0)
                if label_notify['time'] - time.time() > 8:
                    pass
                else:
                    self.main_window.Notify_Label.setText(label_notify['text'])
                    self.label_notify_timer.start(2500)
                    self.label_notify_busy_flag = True

    def Label_notify(self, text):
        self.label_notify_list.append({'text' : text, 'time' : time.time()})

    def On_label_notify_timer_timeout(self):
        self.main_window.Notify_Label.setText('')
        self.label_notify_busy_flag = False


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

    def Set_base_color(self, color):
        r, g, b, _ = color.getRgb()
        self.base_color = QColor(r, g, b)

    def Get_board_color(self):
        return self.board_color

    def Set_board_color(self, color):
        r, g, b, _ = color.getRgb()
        self.board_color = QColor(r, g, b)

    def Get_text_color(self):
        return self.text_color

    def Set_text_color(self, color):
        r, g, b, _ = color.getRgb()
        self.text_color = QColor(r, g, b)


class Event_And_Singal_Distributor:
    def __init__(self, main_window):
        self.main_window = main_window

    def init(self):
        self.main_window.Board_Label.mousePressEvent   = self.board_layer_view.Mouse_press_event
        self.main_window.Board_Label.mouseMoveEvent    = self.board_layer_view.Mouse_move_event
        self.main_window.Board_Label.mouseReleaseEvent = self.board_layer_view.Mouse_release_event


class Main_Window(QMainWindow, Ui_Main_Window_UI):
    def __init__(self):
        super().__init__()

        self.main_window = self

        self.image_edited_flag = False

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
        self.Customize_ui()

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
            module.color_view = self.color_view
            module.color_controller = self.color_controller
            module.tool_view = self.tool_view
            module.tool_controller = self.tool_controller
            module.notify_controller = self.notify_controller
            module.backup_controller = self.backup_controller
            module.style_manage_controller = self.style_manage_controller
            module.event_and_singal_distributor = self.event_and_singal_distributor

        for module in self.module_list:
            module.init()

    def Customize_ui(self):
        self.main_window.Pencil_Size_ComboBox.setStyleSheet('''#Pencil_Size_ComboBox QAbstractItemView{min-width: 60px;}''')

    def Get_style_manage_controller(self):
        return self.style_manage_controller

    def Set_image_edited(self):
        self.image_edited_flag = True



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Main_Window()
    sys.exit(app.exec_())