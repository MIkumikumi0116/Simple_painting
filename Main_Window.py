import sys
import time
import math
import numpy as np
from threading import Thread
from PIL import Image, ImageQt, ImageDraw, ImageOps

from skimage.transform import resize

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QColor
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal, QObject

from Main_Window_UI import Ui_Main_Window_UI
from Custom_Widgets.Layer_Widget.Layer_Widget import Layer_Widget
from Custom_Widgets.Color_Indicator_Widget import Color_Indicator_Widget



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
        self.current_frame.Insert_layer(self.board_layer_controller.Inti_get_first_layer())

    def Get_current_frame(self):
        return self.current_frame


class Board_Layer_View:
    def __init__(self, main_window):
        self.main_window = main_window

        self.camera_image = None

        self.camera_zoom = None
        self.camera_rotate = 30
        self.camera_offset = (0, 0)
        self.camera_board_size = (None ,None)

        self.CAMERMA_ZOOM_MAX = 10
        self.CAMERMA_ZOOM_MIN = -10

    def init(self):
        pass

    def _Init_print_image(self, image):
        # init camera_image, camera_zoom, camera_board_size
        self.camera_image = image.copy()
        image_size = image.size
        label_size = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())
        camera_offset = self.camera_offset

        if image_size[0] <= label_size[0] and image_size[1] <= label_size[1]:
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

        r, g, b, _ = self.style_manage_controller.Get_base_color().getRgb()
        label_background_image = Image.new('RGBA',
                                           (image_transferred.size[0] + label_size[0], image_transferred.size[1] + label_size[1]),
                                           (r, g, b))
        label_background_image.paste(image_transferred, (label_size[0] // 2 ,label_size[1] // 2))

        drawn_rect = [0, 0, 0, 0]
        drawn_rect[0] = label_background_image.size[0] // 2 + camera_offset[0] - label_size[0] // 2
        drawn_rect[1] = label_background_image.size[1] // 2 + camera_offset[1] - label_size[1] // 2
        drawn_rect[2] = drawn_rect[0] + label_size[1]
        drawn_rect[3] = drawn_rect[1] + label_size[1]

        drawn_image = label_background_image.crop(tuple(drawn_rect))

        self.camera_zoom = camera_zoom
        self.camera_board_size = label_background_image.size
        self.Set_h_scrollbar()
        self.Set_v_scrollbar()
        self.main_window.Board_Label.setPixmap(ImageQt.toqpixmap(drawn_image))

    def _Inti_get_first_layer_widget(self):
        return self.main_window.Layer_1_Widget

    def Print_image_archive(self, image):
        # self.camera_zoom = 30
        self.camera_image = image.copy()


        original_image_size = image.size

        camera_zoom   = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
        camera_rotate = self.camera_rotate
        camera_offset = self.camera_offset
        label_size    = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())

        angle    = np.radians(camera_rotate)
        cos, sin = np.cos(angle), np.sin(angle)
        inverse_rotate_matrix = np.array([[ cos, sin],
                                          [-sin, cos]])
        inverse_scale_matrix  = np.array([[1 / camera_zoom, 0],
                                          [0, 1 / camera_zoom]])

        viewport_pos_list = [np.array([-label_size[0] / 2, -label_size[1] / 2]),
                             np.array([ label_size[0] / 2, -label_size[1] / 2]),
                             np.array([-label_size[0] / 2,  label_size[1] / 2]),
                             np.array([ label_size[0] / 2,  label_size[1] / 2])]
        viewport_pos_inverse_transform = lambda viewport_pos: inverse_scale_matrix @ inverse_rotate_matrix @ viewport_pos - np.array([camera_offset[0], camera_offset[1]])
        viewport_pos_list = list(map(viewport_pos_inverse_transform, viewport_pos_list))

        extend = math.ceil((label_size[0] ** 2 + label_size[1] ** 2) ** 0.5 / camera_zoom)
        r, g, b, _ = self.style_manage_controller.Get_base_color().getRgb()
        image = ImageOps.expand(image, border = extend, fill=(r, g, b))

        image_array = np.array(image)
        polygon = [(math.ceil(viewport_pos_list[0][0] + image.size[0] / 2), math.ceil(viewport_pos_list[0][1] + image.size[0] / 2)),
                   (math.ceil(viewport_pos_list[1][0] + image.size[0] / 2), math.ceil(viewport_pos_list[1][1] + image.size[0] / 2)),
                   (math.ceil(viewport_pos_list[3][0] + image.size[0] / 2), math.ceil(viewport_pos_list[3][1] + image.size[0] / 2)),
                   (math.ceil(viewport_pos_list[2][0] + image.size[0] / 2), math.ceil(viewport_pos_list[2][1] + image.size[0] / 2))]
        image_mask = Image.new('1', (image.size[1], image.size[0]), 0)
        ImageDraw.Draw(image_mask).polygon(polygon, outline = 1, fill = 1)
        mask_array = np.array(image_mask)

        image_array[:, :, 3]  = mask_array * 255
        image = Image.fromarray(image_array, "RGBA")
        image = image.crop(image.getbbox())
        image = image.resize((image.size[0] * camera_zoom, image.size[1] * camera_zoom), Image.NEAREST)

        angle    = np.radians(camera_rotate)
        cos, sin = np.cos(angle), np.sin(angle)
        rotate_matrix = np.array([[ cos,-sin],
                                  [ sin, cos]])
        scale_matrix  = np.array([[1 * camera_zoom, 0],
                                  [0, 1 * camera_zoom]])
        viewport_pos_inverse_transform = lambda viewport_pos: scale_matrix @ rotate_matrix @ (viewport_pos + np.array([camera_offset[0], camera_offset[1]])) - np.array([camera_offset[0], camera_offset[1]])
        viewport_pos_list = list(map(viewport_pos_inverse_transform, viewport_pos_list))
        image = image.rotate(-camera_rotate, resample = Image.NEAREST, expand = True, fillcolor = (0, 0, 0, 0))
        image = image.crop((math.ceil(viewport_pos_list[0][0] + image.size[0] / 2),
                            math.ceil(viewport_pos_list[0][1] + image.size[1] / 2),
                            math.ceil(viewport_pos_list[3][0] + image.size[0] / 2),
                            math.ceil(viewport_pos_list[3][1] + image.size[1] / 2)))

        original_image_size_array = np.array([original_image_size[0], original_image_size[1]])
        transferred_image_size = scale_matrix @ rotate_matrix @original_image_size_array

        self.camera_board_size = ((math.ceil(transferred_image_size[0]), math.ceil(transferred_image_size[1])))
        self.Set_h_scrollbar()
        self.Set_v_scrollbar()
        self.main_window.Board_Label.setPixmap(ImageQt.toqpixmap(image))

    def Print_image(self, image):
        self.camera_image = image.copy()

        camera_zoom   = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
        camera_rotate = self.camera_rotate
        camera_offset = self.camera_offset
        label_size    = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())

        r, g, b, _ = self.style_manage_controller.Get_base_color().getRgb()
        image = image.resize((image.size[0] * camera_zoom, image.size[1] * camera_zoom), Image.NEAREST)
        image = image.rotate(-camera_rotate, resample = Image.NEAREST, expand = True, fillcolor = (r, g, b))
        self.camera_board_size = ((image.size[0] + label_size[0], image.size[1] + label_size[1]))

        drawn_rect    = [0, 0, 0, 0]
        drawn_rect[0] = image.size[0] / 2 + camera_offset[0]  - label_size[0] / 2
        drawn_rect[1] = image.size[1] / 2 + camera_offset[1]  - label_size[1] / 2
        drawn_rect[2] = drawn_rect[0] + label_size[0]
        drawn_rect[3] = drawn_rect[1] + label_size[1]

        paste_pos     = [0, 0]
        paste_pos[0]  = 0 if drawn_rect[0] > 0 else math.ceil(-drawn_rect[0])
        paste_pos[1]  = 0 if drawn_rect[1] > 0 else math.ceil(-drawn_rect[1])

        drawn_rect[0] = math.ceil(max(drawn_rect[0], 0))
        drawn_rect[1] = math.ceil(max(drawn_rect[1], 0))
        drawn_rect[2] = math.ceil(min(drawn_rect[2], image.size[0]))
        drawn_rect[3] = math.ceil(min(drawn_rect[3], image.size[1]))

        image = image.crop(tuple(drawn_rect))
        label_background_image = Image.new('RGBA',
                                           (label_size[0], label_size[1]),
                                           (r, g, b))
        label_background_image.paste(image, (paste_pos[0], paste_pos[1]))

        self.Set_h_scrollbar()
        self.Set_v_scrollbar()
        self.main_window.Board_Label.setPixmap(ImageQt.toqpixmap(label_background_image))

    def Label_pos_to_board_pos(self, label_x, label_y):
        camera_zoom       = self.camera_zoom
        camera_rotate     = self.camera_rotate
        camera_offset     = self.camera_offset
        camera_board_size = self.camera_board_size

        board_size =  self.board_layer_controller.Get_board_size()
        label_size = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())

        camera_board_x = camera_board_size[0] / 2 + camera_offset[0] - label_size[0] / 2 + label_x
        camera_board_y = camera_board_size[1] / 2 + camera_offset[1] - label_size[1] / 2 + label_y

        angle         = np.radians(camera_rotate)
        cos, sin      = np.cos(angle), np.sin(angle)
        rotate_matrix = np.array([[ cos, sin],
                                  [-sin, cos]])
        scale_matrix  = np.array([[(1 / camera_zoom) if camera_zoom > 0 else -camera_zoom, 0],
                                  [0, (1 / camera_zoom) if camera_zoom > 0 else -camera_zoom]])

        board_vector  = np.array([float(camera_board_x), float(camera_board_y)])
        board_vector -= np.array([camera_board_size[0] / 2, camera_board_size[1] / 2])
        board_vector  = np.dot(rotate_matrix, board_vector)
        board_vector  = np.dot(scale_matrix, board_vector)
        board_vector += np.array([board_size[0] / 2, board_size[1] / 2])

        return round(board_vector[0]), round(board_vector[1])

    def Get_new_layer_widget(self):
        layer_widget = Layer_Widget(self.main_window.Layer_List_ScrollArea_Widget)
        self.main_window.Layer_List_ScrollArea_Layout.addWidget(layer_widget)
        return layer_widget

    def Zoom_in(self, label_x, label_y):
        if self.camera_zoom + 1 <= self.CAMERMA_ZOOM_MAX:
            original_camera_zoom    = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
            self.camera_zoom        = self.camera_zoom + 1 if self.camera_zoom + 1 not in (0, -1) else 1
            transferred_camera_zoom = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom

            label_size        = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())
            camera_board_size =  self.camera_board_size
            original_offset   =  self.camera_offset

            original_camera_board_x = original_offset[0] - label_size[0] / 2 + label_x
            original_camera_board_y = original_offset[1] - label_size[1] / 2 + label_y

            transferred_camera_board_x = original_camera_board_x / original_camera_zoom * transferred_camera_zoom
            transferred_camera_board_y = original_camera_board_y / original_camera_zoom * transferred_camera_zoom

            transferred_offset_x = transferred_camera_board_x + label_size[0] / 2 - label_x
            transferred_offset_y = transferred_camera_board_y + label_size[0] / 2 - label_y

            self.camera_offset = (round(transferred_offset_x), round(transferred_offset_y))

            angle            = np.radians(self.camera_rotate)
            cos, sin         = np.cos(angle), np.sin(angle)
            rotate_matrix    = np.array([[ cos, sin],
                                         [-sin, cos]])
            image_size_array = np.array([self.camera_image.size[0], self.camera_image.size[1]])
            image_size_array = np.dot(rotate_matrix, image_size_array)
            image_size       = (image_size_array[0], image_size_array[1])
            self.camera_board_size = ((math.ceil(image_size[0] * transferred_camera_zoom) if transferred_camera_zoom > 0 else math.ceil(image_size[0] // -transferred_camera_zoom)) + label_size[0],
                                      (math.ceil(image_size[1] * transferred_camera_zoom) if transferred_camera_zoom > 0 else math.ceil(image_size[1] // -transferred_camera_zoom)) + label_size[1])

            self.Set_h_scrollbar()
            self.Set_v_scrollbar()
            self.Print_image(self.camera_image)

    def Zoom_out(self, label_x, label_y):
        if self.camera_zoom - 1 >= self.CAMERMA_ZOOM_MIN:
            original_camera_zoom    = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
            self.camera_zoom        = self.camera_zoom - 1 if self.camera_zoom - 1 not in (1, 0) else -1
            transferred_camera_zoom = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom

            label_size        = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())
            camera_board_size =  self.camera_board_size
            original_offset   =  self.camera_offset

            original_camera_board_x = original_offset[0] - label_size[0] / 2 + label_x
            original_camera_board_y = original_offset[1] - label_size[1] / 2 + label_y

            transferred_camera_board_x = original_camera_board_x / original_camera_zoom * transferred_camera_zoom
            transferred_camera_board_y = original_camera_board_y / original_camera_zoom * transferred_camera_zoom

            transferred_offset_x = transferred_camera_board_x + label_size[0] / 2 - label_x
            transferred_offset_y = transferred_camera_board_y + label_size[0] / 2 - label_y

            self.camera_offset = (round(transferred_offset_x), round(transferred_offset_y))

            angle            = np.radians(self.camera_rotate)
            cos, sin         = np.cos(angle), np.sin(angle)
            rotate_matrix    = np.array([[ cos, sin],
                                         [-sin, cos]])
            image_size_array = np.array([self.camera_image.size[0], self.camera_image.size[1]])
            image_size_array = np.dot(rotate_matrix, image_size_array)
            image_size       = (image_size_array[0], image_size_array[1])
            self.camera_board_size = ((math.ceil(image_size[0] * transferred_camera_zoom) if transferred_camera_zoom > 0 else math.ceil(image_size[0] // -transferred_camera_zoom)) + label_size[0],
                                      (math.ceil(image_size[1] * transferred_camera_zoom) if transferred_camera_zoom > 0 else math.ceil(image_size[1] // -transferred_camera_zoom)) + label_size[1])

            self.Set_h_scrollbar()
            self.Set_v_scrollbar()
            self.Print_image(self.camera_image)

    def Set_h_scrollbar(self):
        self.main_window.Board_H_ScrollBar.blockSignals(True)
        self.main_window.Board_H_ScrollBar.setRange(  -(self.camera_board_size[0] - self.main_window.Board_Label.width()) // 2,
                                                       (self.camera_board_size[0] - self.main_window.Board_Label.width()) // 2)
        self.main_window.Board_H_ScrollBar.setPageStep((self.camera_board_size[0] - self.main_window.Board_Label.width()) // 15)
        self.main_window.Board_H_ScrollBar.setValue(self.camera_offset[0])
        self.main_window.Board_H_ScrollBar.blockSignals(False)

    def Set_v_scrollbar(self):
        self.main_window.Board_V_ScrollBar.blockSignals(True)
        self.main_window.Board_V_ScrollBar.setRange(  -(self.camera_board_size[1] - self.main_window.Board_Label.height()) // 2,
                                                       (self.camera_board_size[1] - self.main_window.Board_Label.height()) // 2)
        self.main_window.Board_V_ScrollBar.setPageStep((self.camera_board_size[1] - self.main_window.Board_Label.height()) // 15)
        self.main_window.Board_V_ScrollBar.setValue(self.camera_offset[1])
        self.main_window.Board_V_ScrollBar.blockSignals(False)

    def On_Board_h_scrollbar_value_changed(self, value):
        self.camera_offset = (value, self.camera_offset[1])
        self.Print_image(self.camera_image)

    def On_Board_v_scrollbar_value_changed(self, value):
        self.camera_offset = (self.camera_offset[0], value)
        self.Print_image(self.camera_image)

    def Mouse_press_event(self, event):
        label_x, label_y = event.pos().x(), event.pos().y()
        board_x, board_y = self.Label_pos_to_board_pos(label_x, label_y)
        board_size = self.board_layer_controller.Get_board_size()

        if 0 <= board_x < board_size[0] and 0 <= board_y < board_size[1]:
            self.tool_controller.Mouse_press_event(label_x, label_y, board_x, board_y, event)

    def Mouse_move_event(self, event):
        label_x, label_y = event.pos().x(), event.pos().y()
        board_x, board_y = self.Label_pos_to_board_pos(label_x, label_y)
        board_size = self.board_layer_controller.Get_board_size()

        if 0 <= board_x < board_size[0] and 0 <= board_y < board_size[1]:
            self.tool_controller.Mouse_move_event(label_x, label_y, board_x, board_y, event)

    def Mouse_release_event(self, event):
        label_x, label_y = event.pos().x(), event.pos().y()
        board_x, board_y = self.Label_pos_to_board_pos(label_x, label_y)
        board_size = self.board_layer_controller.Get_board_size()

        if 0 <= board_x < board_size[0] and 0 <= board_y < board_size[1]:
            self.tool_controller.Mouse_release_event(label_x, label_y, board_x, board_y, event)

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

    def Get_camera_zoom_max(self):
        return self.CAMERMA_ZOOM_MAX

    def Get_camera_zoom_min(self):
        return self.CAMERMA_ZOOM_MIN


class Board_Layer_Controller:
    class Layer:
        def __init__(self, controller, widget, image = None, offset = (0, 0), name = '', mod_enum = '正常', opacity = 100):
            self.controller = controller
            self.widget = widget
            self.widget.init(self)
            self.widget.Hide_Button.clicked.connect(self.On_hide_button_clicked)
            self.widget.Lock_Button.clicked.connect(self.On_lock_button_clicked)

            self.image = image if image != None else Image.new('RGBA',
                                                               self.controller.Get_board_size(),
                                                              (255, 255, 255, 0))
            self.offset = offset

            self.hide_flag = False
            self.lock_flag = False
            self.name = name if name != '' else f'图层{controller._Get_next_layer_index_self_add()}'
            self.mod_enum = mod_enum
            self.opacity = opacity

            self.Set_preview_label()
            self.widget.Set_widget_info()

        def Set_preview_label(self):
            r, g, b, _ = self.controller._Get_base_color().getRgb()
            preview_background_image = Image.new('RGBA',
                                                  self.widget.Get_preview_label_size(),
                                                 (r, g, b))

            preview_image = self.image.copy()
            preview_image.putalpha(255)
            if self.image.size[0] / preview_background_image.size[0] == self.image.size[1] / preview_background_image.size[1]:
                preview_image = preview_image.resize((preview_background_image.size[0], preview_background_image.size[1]))
                preview_background_image.paste(preview_image, (0, 0))
            elif self.image.size[0] / preview_background_image.size[0] > self.image.size[1] / preview_background_image.size[1]:
                preview_image = preview_image.resize(
                                                    (preview_background_image.size[0],
                                               round(preview_image.size[1] * preview_background_image.size[0] / preview_image.size[0])))
                preview_background_image.paste(preview_image, (0, (preview_background_image.size[1] - preview_image.size[1]) // 2))
            else:
                preview_image = preview_image.resize((
                                               round(preview_image.size[0] * preview_background_image.size[1] / preview_image.size[1]),
                                                     preview_background_image.size[1]))
                preview_background_image.paste(preview_image, ((preview_background_image.size[0] - preview_image.size[0]) // 2, 0))

            self.widget.Set_preview_label(preview_background_image)

        def Get_layer_size(self):
            return self.image.size

        def On_hide_button_clicked(self):
            self.hide_flag = not self.hide_flag
            self.widget.Set_widget_info()
            self.controller.Draw_painting()

        def On_lock_button_clicked(self):
            self.lock_flag = not self.lock_flag
            self.widget.Set_widget_info()

    def __init__(self, main_window):
        self.main_window = main_window

        self.board_size = (256, 256)
        self.current_frame = None
        self.layer_list = None
        self.selected_layer_list = None
        self.background_layer = Image.new('RGBA', self.board_size, (255, 255, 255))

        self.next_layer_index = 1

    def init(self):
        self.current_frame = self.frame_controller.Get_current_frame()
        self.layer_list = self.current_frame.layer_list
        self.selected_layer_list = [self.layer_list[0]]

        painting = self.background_layer.copy()
        for layer in self.layer_list:
            if not layer.hide_flag:
                layer_image = layer.image.copy()

                if layer.offset[0] < 0:
                    layer_image = layer_image.crop((-layer.offset[0], 0, layer_image.size[0], layer_image.size[1]))
                if layer.offset[1] < 0:
                    layer_image = layer_image.crop((0, -layer.offset[1], layer_image.size[0], layer_image.size[1]))
                if layer.offset[0] + layer_image.size[0] > self.board_size[0]:
                    layer_image = layer_image.crop((0, 0, layer.offset[0] + layer_image.size[0] - self.board_size[0], layer_image.size[1]))
                if layer.offset[1] + layer_image.size[1] > self.board_size[1]:
                    layer_image = layer_image.crop((0, 0, layer_image.size[0], layer.offset[1] + layer_image.size[1] - self.board_size[1]))

                if layer.mod_enum == '正常':
                    painting.paste(layer.image,
                                  (layer.offset[0] if layer.offset[0] >= 0 else 0,
                                   layer.offset[1] if layer.offset[1] >= 0 else 0),
                                   mask = layer.image)

        self.board_layer_view._Init_print_image(painting)

    def Inti_get_first_layer(self):
        return Board_Layer_Controller.Layer(self, self.board_layer_view._Inti_get_first_layer_widget(), name = '图层1')

    def Draw_painting(self):
        painting = self.background_layer.copy()
        for layer in self.layer_list:
            if not layer.hide_flag:
                layer_image = layer.image.copy()

                if layer.offset[0] < 0:
                    layer_image = layer_image.crop((-layer.offset[0], 0, layer_image.size[0], layer_image.size[1]))
                if layer.offset[1] < 0:
                    layer_image = layer_image.crop((0, -layer.offset[1], layer_image.size[0], layer_image.size[1]))
                if layer.offset[0] + layer_image.size[0] > self.board_size[0]:
                    layer_image = layer_image.crop((0, 0, layer.offset[0] + layer_image.size[0] - self.board_size[0], layer_image.size[1]))
                if layer.offset[1] + layer_image.size[1] > self.board_size[1]:
                    layer_image = layer_image.crop((0, 0, layer_image.size[0], layer.offset[1] + layer_image.size[1] - self.board_size[1]))

                if layer.mod_enum == '正常':
                    painting.paste(layer.image,
                                  (layer.offset[0] if layer.offset[0] >= 0 else 0,
                                   layer.offset[1] if layer.offset[1] >= 0 else 0),
                                   mask = layer.image)

        self.board_layer_view.Print_image(painting)

    def Get_new_layer(self):
        return Board_Layer_Controller.Layer(self, self.board_layer_view.Get_new_layer_widget())

    def _Get_next_layer_index_self_add(self):
        self.next_layer_index += 1
        return self.next_layer_index - 1

    def _Get_base_color(self):
        return self.style_manage_controller.Get_base_color()

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
            if layer.lock_flag:
                self.controller._Send_label_notify('该图层已锁定')
                return

            self.controller._Set_image_edited()

            layer_x = x - layer.offset[0]
            layer_y = y - layer.offset[1]

            if 0 <= layer_x < layer.image.size[0] and 0 <= y < layer.image.size[1]:
                radius = self.brush_size // 2
                board_size = self.controller._Get_board_size()
                pixel_matrix_np = np.array(layer.image, dtype = 'uint8')
                r, g, b, _ = self.controller._Get_front_color().getRgb()
                color = np.array((r, g, b, 255))

                # TODO 插值
                paint_area = [(i, j) for i in range(layer_x - radius, layer_x + radius + 1)
                                     for j in range(layer_y - radius, layer_y + radius + 1)
                                     if abs(i - layer_x) ** 2 + abs(j - layer_y) ** 2 <= radius ** 2
                                     and 0 <= i < board_size[0]
                                     and 0 <= j < board_size[1]]

                for point in paint_area:
                    pixel_matrix_np[point[1], point[0]] = color

                layer.image = Image.fromarray(pixel_matrix_np)

                self.controller._Draw_painting()

        def Mouse_press_event(self, x, y, event):
            if event.buttons() == Qt.LeftButton:
                self.Pencil_draw(x, y)

        def Mouse_move_event(self, x, y, event):
            if event.buttons() == Qt.LeftButton:
                self.Pencil_draw(x, y)

        def Mouse_release_event(self, x, y, event):
            if event.buttons() == Qt.LeftButton:
                self.Pencil_draw(x, y)

    def __init__(self, main_window):
        self.main_window = main_window

        self.current_tool = None

        self.pencil_tool = Tool_Controller.Pencil_Tool(self)

        self.board_pos_only_list = [self.pencil_tool]

    def init(self):
        self.current_tool = self.pencil_tool

    def Mouse_press_event(self, label_x, label_y, board_x, board_y, event):
        if self.current_tool in self.board_pos_only_list:
            self.current_tool.Mouse_press_event(board_x, board_y, event)

    def Mouse_move_event(self, label_x, label_y, board_x, board_y, event):
        if self.current_tool in self.board_pos_only_list:
            self.current_tool.Mouse_move_event(board_x, board_y, event)

    def Mouse_release_event(self, label_x, label_y, board_x, board_y, event):
        if self.current_tool in self.board_pos_only_list:
            self.current_tool.Mouse_release_event(board_x, board_y, event)

    def _Get_selected_layer(self):
        return self.board_layer_controller.Get_selected_layer()

    def _Send_label_notify(self, text):
        self.notify_controller.New_label_notify(text)

    def _Set_image_edited(self):
        self.main_window.Set_image_edited_flag(True)

    def _Get_board_size(self):
        return self.board_layer_controller.Get_board_size()

    def _Get_front_color(self):
        return self.color_controller.Get_front_color()

    def _Draw_painting(self):
        self.board_layer_controller.Draw_painting()


class Color_Controller:
    def __init__(self, main_window):
        self.main_window = main_window

        self.front_color = QColor(0, 0, 0)
        self.back_color  = QColor(255, 255, 255)

    def init(self):
        self.main_window.Color_Picker_Widget.color_change_singal.connect(self.On_color_change_singal_emit)
        self.main_window.Color_Indicator_Widget.switch_color_singal.connect(self.On_switch_color_singal_emit)

    def On_color_change_singal_emit(self, color):
        r, g, b, _ = color.getRgb()
        self.front_color.setRgb(r, g, b)
        self.main_window.Color_Indicator_Widget.Set_front_color(self.front_color)

    def On_switch_color_singal_emit(self):
        self.front_color, self.back_color = self.back_color, self.front_color

        self.main_window.Color_Indicator_Widget.Set_front_color(self.front_color)
        self.main_window.Color_Indicator_Widget.Set_back_color(self.back_color)
        self.main_window.Color_Picker_Widget.Set_current_color(self.front_color)

    def Get_front_color(self):
        return self.front_color

    def Set_front_color(self, color):
        r, g, b, _ = color.getRgb()
        self.front_color.setRgb(r, g, b)

        self.main_window.Color_Indicator_Widget.Set_front_color(self.front_color)
        self.main_window.Color_Picker_Widget.Set_current_color(self.front_color)

    def Get_back_color(self):
        return self.back_color

    def Set_back_color(self, color):
        r, g, b, _ = color.getRgb()
        self.back_color.setRgb(r, g, b)

        self.main_window.Color_Indicator_Widget.Set_back_color(self.back_color)


class Notify_Controller(QObject):
    label_notify_singal = pyqtSignal(str)

    def __init__(self, main_window):
        self.main_window = main_window
        super().__init__()

        self.label_notify_list = []
        self.label_notify_thread = Thread(target = self.Label_notify_thread_action, args = ())
        self.label_notify_thread.start()
        self.label_notify_singal.connect(self.Release_label_notify)
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
                    self.label_notify_singal.emit(label_notify['text'])

    def New_label_notify(self, text):
        self.label_notify_list.append({'text' : text, 'time' : time.time()})

    def Release_label_notify(self, text):
        self.main_window.Notify_Label.setText(text)
        self.label_notify_busy_flag = True
        self.label_notify_timer.start(2500)

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
        self.main_window.keyPressEvent                 = self.Main_window_key_press_event
        self.main_window.keyReleaseEvent               = self.Main_window_key_release_event
        self.main_window.wheelEvent                    = self.Main_window_wheel_event
        self.main_window.Board_Label.mousePressEvent   = self.board_layer_view.Mouse_press_event
        self.main_window.Board_Label.mouseMoveEvent    = self.board_layer_view.Mouse_move_event
        self.main_window.Board_Label.mouseReleaseEvent = self.board_layer_view.Mouse_release_event

        self.main_window.Board_H_ScrollBar.valueChanged.connect(self.board_layer_view.On_Board_h_scrollbar_value_changed)
        self.main_window.Board_V_ScrollBar.valueChanged.connect(self.board_layer_view.On_Board_v_scrollbar_value_changed)

    def Main_window_wheel_event(self, event):
        if self.main_window.Board_Label.rect().contains(event.pos()):
            label_x, label_y  = event.position().x(), event.position().y()

            if event.angleDelta().y() > 0:
                self.board_layer_view.Zoom_in(label_x, label_y)
            else:
                self.board_layer_view.Zoom_out(label_x, label_y)

    def Main_window_key_press_event(self, event):
        if event.key() == Qt.Key_Space:
            self.main_window.Set_key_space_pressed_flag(True)

    def Main_window_key_release_event(self, event):
        if event.key() == Qt.Key_Space:
            self.main_window.Set_key_space_pressed_flag(False)


class Main_Window(QMainWindow, Ui_Main_Window_UI):
    def __init__(self):
        super().__init__()

        self.main_window = self

        self.image_edited_flag = False
        self.key_space_pressed_flag = False

        self.frame_view = Frame_View(self.main_window)
        self.frame_controller = Frame_Controller(self.main_window)
        self.board_layer_view = Board_Layer_View(self.main_window)
        self.board_layer_controller = Board_Layer_Controller(self.main_window)
        self.tool_view = Tool_View(self.main_window)
        self.tool_controller = Tool_Controller(self.main_window)
        self.color_controller = Color_Controller(self.main_window)
        self.notify_controller = Notify_Controller(self.main_window)
        self.backup_controller = Backup_Controller(self.main_window)
        self.style_manage_controller = Style_Manage_Controller(self.main_window)
        self.event_and_singal_distributor = Event_And_Singal_Distributor(self.main_window)

        self.setupUi(self)
        self.main_window.show()
        self.init()

        self.module_list = [self.frame_view,
                            self.frame_controller,
                            self.board_layer_view,
                            self.board_layer_controller,
                            self.tool_view,
                            self.tool_controller,
                            self.color_controller,
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
            module.color_controller = self.color_controller
            module.notify_controller = self.notify_controller
            module.backup_controller = self.backup_controller
            module.style_manage_controller = self.style_manage_controller
            module.event_and_singal_distributor = self.event_and_singal_distributor

        for module in self.module_list:
            module.init()

    def init(self):
        self.main_window.Pencil_Size_ComboBox.setStyleSheet('''#Pencil_Size_ComboBox QAbstractItemView{min-width: 60px;}''')
        self.main_window.Board_Label_Widget.setStyleSheet('''#Board_Label_Widget{border:1px solid red}''')

        self.Color_Indicator_Widget = Color_Indicator_Widget(self)
        self.main_window.Quick_Func_Layout.addWidget(self.Color_Indicator_Widget, 0, 5, 2, 1, Qt.AlignHCenter)

    def Get_style_manage_controller(self):
        return self.style_manage_controller

    def Get_image_edited_flag(self):
        return self.image_edited_flag

    def Set_image_edited_flag(self, flag):
        self.image_edited_flag = flag

    def Get_key_space_pressed_flag(self):
        return self.key_space_pressed_flag

    def Set_key_space_pressed_flag(self, flag):
        self.key_space_pressed_flag = flag



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Main_Window()
    sys.exit(app.exec_())