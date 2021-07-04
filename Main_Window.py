import re
import os
import sys
import time
import copy
import json
import base64
import numpy as np
from io import BytesIO
from threading import Thread
from PIL import Image, ImageQt, ImageDraw, ImageOps

from PyQt5.QtWidgets import QApplication, QMainWindow, QSpacerItem, QSizePolicy, QStyledItemDelegate, QFileDialog
from PyQt5.QtGui import QImage, QColor, QPainter, QPen, QPolygon, QPixmap, QTransform, QBrush, QPainterPath, QPalette, QIcon
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal, QObject, QSize
from PyQt5 import sip

from Main_Window_UI import Ui_Main_Window_UI
from Custom_Widgets.Layer_Widget.Layer_Widget import Layer_Widget
from Custom_Widgets.Color_Indicator_Widget import Color_Indicator_Widget

#TODO 图层拖动排序

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
            self.selected_layer_list = []

        def Insert_layer(self, layer, index = None):
            if index is None:
                self.layer_list.append(layer)
            else:
                self.layer_list.insert(index, layer)

        def Insert_layer_and_select(self, layer, index = None):
            if index is None:
                self.layer_list.append(layer)
            else:
                self.layer_list.insert(index, layer)

            self.selected_layer_list = [layer]

        def Move_up_layer(self, layer):
            layer_index = self.layer_list.index(layer)
            if layer_index > 0:
                self.layer_list[layer_index - 1], self.layer_list[layer_index] = \
                self.layer_list[layer_index], self.layer_list[layer_index - 1]

        def Move_down_layer(self, layer):
            layer_index = self.layer_list.index(layer)
            if layer_index < len(self.layer_list) - 1:
                self.layer_list[layer_index + 1], self.layer_list[layer_index] = \
                self.layer_list[layer_index], self.layer_list[layer_index + 1]

        def Append_selected_layer(self, layer):
            if layer not in self.selected_layer:
                self.selected_layer.append(layer)


        def Get_layer_list(self):
            return self.layer_list

        def Get_strong_selected_layer(self):
            if len(self.selected_layer_list) > 0:
                return self.selected_layer_list[0]
            else:
                return False

        def Get_strong_selected_layer_index(self):
            if len(self.selected_layer_list) > 0:
                return self.layer_list.index(self.selected_layer_list[0])
            else:
                return False

        def Get_selected_layer_list(self):
            return self.selected_layer_list

        def Get_selected_layer_index_list(self):
            index_list = []
            for layer in self.selected_layer_list:
                index_list.append(self.layer_list.index(layer))

            return index_list

        def Set_selected_layer(self, index_list):
            self.selected_layer_list = []
            for index in index_list:
                self.selected_layer_list.append(self.layer_list[index])

        def Delete_layer(self, layer):
            self.layer_list.remove(layer)
            if layer in self.selected_layer_list:
                self.selected_layer_list.remove(layer)


    def __init__(self, main_window):
        self.main_window = main_window

        self.frame_list = []
        self.current_frame = None

    def init(self):
        self.frame_list = []
        self.current_frame = None


    def Get_frame_list(self):
        return self.frame_list

    def Set_frame_list(self, frame_list):
        self.frame_list = frame_list
        self.current_frame = self.frame_list[0]

    def Get_current_frame(self):
        return self.current_frame

    def Set_current_frame(self, index):
        self.current_frame = self.frame_list[index]


class Board_Layer_View:
    def __init__(self, main_window):
        self.main_window = main_window

        self.board_image       = None #缩放旋转平移前的图片

        self.camera_zoom       = None
        self.camera_rotate     = 0
        self.camera_offset     = (0, 0)
        self.camera_board_size = (None ,None)   #缩放旋转平移后的图片尺寸

        self.rotate_first_pos  = None
        self.rotate_second_pos = None
        self.drag_first_pos    = None
        self.drag_second_pos   = None

        self.CAMERMA_ZOOM_MAX  = 50
        self.CAMERMA_ZOOM_MIN  = -20

    def init(self):
        self.board_image       = None
        self.camera_zoom       = None
        self.camera_board_size = None

        self.rotate_first_pos  = None
        self.rotate_second_pos = None
        self.drag_first_pos    = None
        self.drag_second_pos   = None


    def Print_image(self, image):
        self.board_image = image.copy()

        camera_zoom   =  self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
        camera_rotate =  self.camera_rotate
        camera_offset =  self.camera_offset
        label_size    = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())

        if self.camera_board_size[0] > label_size[0] or self.camera_board_size[1] > label_size[1]:
            angle    = np.radians(camera_rotate)
            cos, sin = np.cos(angle), np.sin(angle)
            inverse_rotate_matrix = np.array([[ cos, sin],
                                              [-sin, cos]])
            inverse_scale_matrix  = np.array([[1 / camera_zoom, 0],
                                             [0, 1 / camera_zoom]])
            camera_offset_array   = np.array([float(camera_offset[0]), float(camera_offset[1])])
            camera_offset_array   = inverse_scale_matrix @ inverse_rotate_matrix @ camera_offset_array

            viewport_pos_list = [np.array([-label_size[0] / 1.8, -label_size[1] / 1.8]),
                                 np.array([ label_size[0] / 1.8, -label_size[1] / 1.8]),
                                 np.array([-label_size[0] / 1.8,  label_size[1] / 1.8]),
                                 np.array([ label_size[0] / 1.8,  label_size[1] / 1.8])]
            viewport_pos_inverse_transform = lambda viewport_pos_array : (inverse_scale_matrix @ inverse_rotate_matrix @ viewport_pos_array) + camera_offset_array
            viewport_pos_list = list(map(viewport_pos_inverse_transform, viewport_pos_list))

            board_extend = (label_size[0] ** 2 + label_size[1] ** 2) ** 0.5 / camera_zoom * 1.2
            image        = ImageOps.expand(image, border = round(board_extend), fill=(0, 0, 0, 0))

            image_array  = np.array(image)
            image_mask   = Image.new('1', (image.size[0], image.size[1]), 0)
            mask_polygon = [(round(viewport_pos_list[0][0] + image.size[0] / 2), round(viewport_pos_list[0][1] + image.size[1] / 2)),
                            (round(viewport_pos_list[1][0] + image.size[0] / 2), round(viewport_pos_list[1][1] + image.size[1] / 2)),
                            (round(viewport_pos_list[3][0] + image.size[0] / 2), round(viewport_pos_list[3][1] + image.size[1] / 2)),
                            (round(viewport_pos_list[2][0] + image.size[0] / 2), round(viewport_pos_list[2][1] + image.size[1] / 2))]
            ImageDraw.Draw(image_mask).polygon(mask_polygon, outline = 1, fill = 1)
            mask_array   = np.array(image_mask)

            image_array[:, :, 0] *= mask_array
            image_array[:, :, 1] *= mask_array
            image_array[:, :, 2] *= mask_array
            image_array[:, :, 3] *= mask_array

            r, g, b, _  = self.style_manage_controller.Get_highlight_back_color().getRgb()
            image_array[(image_array[:, :, 3] == 0) & mask_array] = np.array([r, g, b, 255])

            image = Image.fromarray(image_array, 'RGBA')
            image = image.crop(image.getbbox())
            image = image.resize((round(image.size[0] * camera_zoom), round(image.size[1] * camera_zoom)), Image.NEAREST)
            image = image.rotate(-camera_rotate, resample = Image.NEAREST, expand = True, fillcolor = (0, 0, 0, 0))

            viewport_pos_list = [np.array([-label_size[0] / 2, -label_size[1] / 2]),
                                 np.array([ label_size[0] / 2, -label_size[1] / 2]),
                                 np.array([-label_size[0] / 2,  label_size[1] / 2]),
                                 np.array([ label_size[0] / 2,  label_size[1] / 2])]
            image = image.crop((round(viewport_pos_list[0][0] + image.size[0] / 2),
                                round(viewport_pos_list[0][1] + image.size[1] / 2),
                                round(viewport_pos_list[3][0] + image.size[0] / 2),
                                round(viewport_pos_list[3][1] + image.size[1] / 2)))
        else:
            image = image.resize((round(image.size[0] * camera_zoom), round(image.size[1] * camera_zoom)), Image.NEAREST)
            image = image.rotate(-camera_rotate, resample = Image.NEAREST, expand = True, fillcolor = (0, 0, 0, 0))

            viewport_pos_list = [np.array([-label_size[0] / 2, -label_size[1] / 2]),
                                 np.array([ label_size[0] / 2, -label_size[1] / 2]),
                                 np.array([-label_size[0] / 2,  label_size[1] / 2]),
                                 np.array([ label_size[0] / 2,  label_size[1] / 2])]
            image = image.crop((round(viewport_pos_list[0][0] + image.size[0] / 2 + camera_offset[0]),
                                round(viewport_pos_list[0][1] + image.size[1] / 2 + camera_offset[1]),
                                round(viewport_pos_list[3][0] + image.size[0] / 2 + camera_offset[0]),
                                round(viewport_pos_list[3][1] + image.size[1] / 2 + camera_offset[1])))

            r, g, b, _ = self.style_manage_controller.Get_highlight_back_color().getRgb()
            image_array = np.array(image)
            image_array[:, :, :][image_array[:, :, 3] == 0] = np.array([r, g, b, 255])
            image = Image.fromarray(image_array)

        image = self.Print_promet_layer(image)
        self.main_window.Board_Label.setPixmap(QPixmap(image.toqpixmap()))

    def Print_promet_layer(self, image):
        command = self.board_layer_controller.Get_promet_layer_command()
        if command is None:
            return image

        label_size    = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())

        if command.command_enum == 'draw_rect_solid_line':
            board_first_pos  = command.first_pos
            board_second_pos = command.second_pos

            vertex_pos_list  = [(board_first_pos[0],  board_first_pos[1]),
                                (board_second_pos[0], board_first_pos[1]),
                                (board_second_pos[0], board_second_pos[1]),
                                (board_first_pos[0],  board_second_pos[1])]
            vertex_pos_list  = map(lambda vertex_pos : self.Board_pos_to_label_pos(vertex_pos), vertex_pos_list)
            vertex_pos_list  = list(map(lambda vertex_pos : QPoint(vertex_pos[0], vertex_pos[1]), vertex_pos_list))

            promet_image = QImage(label_size[0], label_size[1], QImage.Format_ARGB32)
            painter      = QPainter(promet_image)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QPen(QColor(0, 0, 0, 255)))
            painter.drawPolygon(QPolygon(vertex_pos_list))
            painter.end()

            promet_image = ImageQt.fromqimage(promet_image)
            image.paste(promet_image, mask = promet_image)
            return image

        elif command.command_enum == 'draw_rect_dotted_line':
            board_first_pos  = command.first_pos
            board_second_pos = command.second_pos

            vertex_pos_list  = [(board_first_pos[0],  board_first_pos[1]),
                                (board_second_pos[0], board_first_pos[1]),
                                (board_second_pos[0], board_second_pos[1]),
                                (board_first_pos[0],  board_second_pos[1])]
            vertex_pos_list  = map(lambda vertex_pos : self.Board_pos_to_label_pos(vertex_pos), vertex_pos_list)
            vertex_pos_list  = list(map(lambda vertex_pos : QPoint(vertex_pos[0], vertex_pos[1]), vertex_pos_list))

            promet_image = QImage(label_size[0], label_size[1], QImage.Format_ARGB32)
            painter      = QPainter(promet_image)
            painter.setRenderHint(QPainter.Antialiasing)
            pen          = QPen(QColor(0, 0, 0, 255))
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.drawPolygon(QPolygon(vertex_pos_list))
            painter.end()

            promet_image = ImageQt.fromqimage(promet_image)
            image.paste(promet_image, mask = promet_image)
            return image

    def Print_image_new_project(self, image):
        # 新建工程后确定初始缩放比例，同时初始化旋转平移等
        # init board_image, camera_zoom, camera_board_size
        self.board_image = image.copy()

        self.camera_zoom       = None
        self.camera_rotate     = 0
        self.camera_offset     = (0, 0)
        self.camera_board_size = (None ,None)

        self.first_click_pos   = None
        self.second_click_pos  = None
        self.drag_first_pos    = None
        self.drag_second_pos   = None

        image_size = image.size
        label_size = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())

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
        elif narrow_type == 'h_narrow':
            camera_zoom = -(image_size[0] // label_size[0] + 1)
        elif narrow_type == 'v_narrow':
            camera_zoom = -(image_size[1] // label_size[1] + 1)

        self.camera_zoom = camera_zoom
        self.Update_camera_board_size()
        self.Set_h_scrollbar()
        self.Set_v_scrollbar()
        self.Update_layer_widget_list()
        self.Print_image(image)


    def Zoom_in(self, mouse_pos):
        if self.camera_zoom + 1 <= self.CAMERMA_ZOOM_MAX:
            original_camera_zoom    = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
            self.camera_zoom        = self.camera_zoom + 1 if self.camera_zoom + 1 not in (0, -1) else 1
            transferred_camera_zoom = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom

            label_size      = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())
            original_offset =  self.camera_offset

            original_board_offset_x    = original_offset[0] - label_size[0] / 2 + mouse_pos[0]
            original_board_offset_y    = original_offset[1] - label_size[1] / 2 + mouse_pos[1]

            transferred_board_offset_x = original_board_offset_x / original_camera_zoom * transferred_camera_zoom
            transferred_board_offset_y = original_board_offset_y / original_camera_zoom * transferred_camera_zoom

            transferred_offset_x       = transferred_board_offset_x + label_size[0] / 2 - mouse_pos[0]
            transferred_offset_y       = transferred_board_offset_y + label_size[1] / 2 - mouse_pos[1]

            self.Update_camera_board_size()

            transferred_offset_x       = max(-self.camera_board_size[0], min(transferred_offset_x, self.camera_board_size[0]))
            transferred_offset_y       = max(-self.camera_board_size[1], min(transferred_offset_y, self.camera_board_size[1]))
            self.camera_offset         = (round(transferred_offset_x), round(transferred_offset_y))

            self.Set_h_scrollbar()
            self.Set_v_scrollbar()
            self.Print_image(self.board_image)

    def Zoom_out(self, mouse_pos):
        if self.camera_zoom - 1 >= self.CAMERMA_ZOOM_MIN:
            original_camera_zoom    = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
            self.camera_zoom        = self.camera_zoom - 1 if self.camera_zoom - 1 not in (1, 0) else -1
            transferred_camera_zoom = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom

            label_size      = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())
            original_offset =  self.camera_offset

            original_board_offset_x    = original_offset[0] - label_size[0] / 2 + mouse_pos[0]
            original_board_offset_y    = original_offset[1] - label_size[1] / 2 + mouse_pos[1]

            transferred_board_offset_x = original_board_offset_x / original_camera_zoom * transferred_camera_zoom
            transferred_board_offset_y = original_board_offset_y / original_camera_zoom * transferred_camera_zoom

            transferred_offset_x       = transferred_board_offset_x + label_size[0] / 2 - mouse_pos[0]
            transferred_offset_y       = transferred_board_offset_y + label_size[1] / 2 - mouse_pos[1]

            self.Update_camera_board_size()

            transferred_offset_x       = max(-self.camera_board_size[0], min(transferred_offset_x, self.camera_board_size[0]))
            transferred_offset_y       = max(-self.camera_board_size[1], min(transferred_offset_y, self.camera_board_size[1]))
            self.camera_offset         = (round(transferred_offset_x), round(transferred_offset_y))

            self.Set_h_scrollbar()
            self.Set_v_scrollbar()
            self.Print_image(self.board_image)

    def Rotate_board(self, delta_angle):
        camera_zoom     =  self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
        camera_rotate   =  self.camera_rotate
        original_offset =  self.camera_offset

        angle    = np.radians(camera_rotate)
        cos, sin = np.cos(angle), np.sin(angle)
        inverse_rotate_matrix = np.array([[ cos, sin],
                                          [-sin, cos]])
        inverse_scale_matrix  = np.array([[1 / camera_zoom, 0],
                                          [0, 1 / camera_zoom]])
        camera_offset = np.array([float(original_offset[0]), float(original_offset[1])])
        board_offset  = inverse_scale_matrix @ inverse_rotate_matrix @ camera_offset

        camera_rotate = camera_rotate + delta_angle

        angle    = np.radians(camera_rotate)
        cos, sin = np.cos(angle), np.sin(angle)
        rotate_matrix = np.array([[cos, -sin],
                                  [sin,  cos]])
        scale_matrix  = np.array([[camera_zoom, 0],
                                  [0, camera_zoom]])
        camera_offset = scale_matrix @ rotate_matrix @ board_offset


        self.camera_rotate = camera_rotate
        self.camera_offset = (round(camera_offset[0]), round(camera_offset[1]))

        self.Update_camera_board_size()
        self.Set_h_scrollbar()
        self.Set_v_scrollbar()
        self.Print_image(self.board_image)

    def Update_offset(self, offset):
        self.camera_offset = offset
        self.Set_h_scrollbar()
        self.Set_v_scrollbar()
        self.Print_image(self.board_image)


    def Label_pos_to_board_pos(self, label_pos):
        camera_zoom   =  self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
        camera_rotate =  self.camera_rotate
        camera_offset =  self.camera_offset
        board_size    =  self.board_layer_controller.Get_board_size()
        label_size    = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())

        camera_board_x = camera_offset[0] - label_size[0] / 2 + label_pos[0]
        camera_board_y = camera_offset[1] - label_size[1] / 2 + label_pos[1]

        angle          = np.radians(camera_rotate)
        cos, sin       = np.cos(angle), np.sin(angle)
        inverse_rotate_matrix = np.array([[ cos, sin],
                                          [-sin, cos]])
        inverse_scale_matrix  = np.array([[1 / camera_zoom , 0],
                                          [0, 1 / camera_zoom]])
        board_array = np.array([float(camera_board_x), float(camera_board_y)])
        board_array = inverse_rotate_matrix @ inverse_scale_matrix @ board_array + np.array([board_size[0] / 2, board_size[1] / 2])

        return (round(board_array[0]), round(board_array[1]))

    def Board_pos_to_label_pos(self, board_pos):
        camera_zoom   =  self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
        camera_rotate =  self.camera_rotate
        camera_offset =  self.camera_offset
        board_size    =  self.board_layer_controller.Get_board_size()
        label_size    = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())

        angle         = np.radians(camera_rotate)
        cos, sin      = np.cos(angle), np.sin(angle)
        rotate_matrix = np.array([[cos, -sin],
                                  [sin,  cos]])
        scale_matrix  = np.array([[camera_zoom, 0],
                                  [0, camera_zoom]])
        offset_array  = np.array([float(camera_offset[0]), float(camera_offset[1])])
        label_center_array = np.array([float(label_size[0] / 2), float(label_size[1] / 2)])

        board_array = np.array([board_pos[0] - board_size[0] / 2, board_pos[1] - board_size[1] / 2])
        label_array = scale_matrix @ rotate_matrix @ board_array - offset_array + label_center_array

        return (round(label_array[0]), round(label_array[1]))

    def Update_camera_board_size(self):
        camera_zoom   = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
        camera_rotate = self.camera_rotate
        image_size    = self.board_image.size

        angle         = np.radians(camera_rotate)
        cos, sin      = np.cos(angle), np.sin(angle)
        rotate_matrix = np.array([[cos,-sin],
                                  [sin, cos]])
        scale_matrix  = np.array([[1 * camera_zoom, 0],
                                  [0, 1 * camera_zoom]])

        diagonal_1_array = np.array([image_size[0],  image_size[1]])
        diagonal_2_array = np.array([image_size[0], -image_size[1]])

        transferred_diagonal_1 = scale_matrix @ rotate_matrix @ diagonal_1_array
        transferred_diagonal_2 = scale_matrix @ rotate_matrix @ diagonal_2_array

        self.camera_board_size = ((round(max(abs(transferred_diagonal_1[0]), abs(transferred_diagonal_2[0]))),
                                   round(max(abs(transferred_diagonal_1[1]), abs(transferred_diagonal_2[1])))))

    def Rotate_board_by_mouse(self, mouse_pos, first_point_flag):
        if first_point_flag:
            self.rotate_first_pos = mouse_pos
            return

        self.rotate_second_pos = mouse_pos

        if (self.rotate_first_pos[0] - self.rotate_second_pos[0]) ** 2 + \
           (self.rotate_first_pos[1] - self.rotate_second_pos[1]) ** 2 > 100:
            first_pos  = self.rotate_first_pos
            second_pos = self.rotate_second_pos
            center_pos = (self.main_window.Board_Label.width() / 2, self.main_window.Board_Label.height() / 2)

            first_pos_vector  = np.array([first_pos[0]  - center_pos[0], first_pos[1]  - center_pos[1]])
            second_pos_vector = np.array([second_pos[0] - center_pos[0], second_pos[1] - center_pos[1]])

            first_len   = np.sqrt(first_pos_vector  @ first_pos_vector )
            second_len  = np.sqrt(second_pos_vector @ second_pos_vector)

            angle_cos   = first_pos_vector @ second_pos_vector / (first_len * second_len)
            delta_angle = np.arccos(angle_cos)
            delta_angle = delta_angle * 360 / 2 / np.pi

            if abs(delta_angle) > 10:
                if np.cross(first_pos_vector, second_pos_vector) > 0:
                    self.Rotate_board( delta_angle // 10 * 10)
                else:
                    self.Rotate_board(-delta_angle // 10 * 10)

                self.rotate_first_pos = self.rotate_second_pos

    def Drag_board_by_mouse(self, mouse_pos, first_point_flag):
        if first_point_flag:
            self.drag_first_pos = mouse_pos
            return

        self.drag_second_pos = mouse_pos

        delta_offset = (self.drag_first_pos[0] - self.drag_second_pos[0], self.drag_first_pos[1] - self.drag_second_pos[1])

        new_offset_x = self.camera_offset[0]  + delta_offset[0]
        new_offset_y = self.camera_offset[1]  + delta_offset[1]
        new_offset_x = max(-self.camera_board_size[0] // 2, min(new_offset_x, (self.camera_board_size[0]) // 2))
        new_offset_y = max(-self.camera_board_size[1] // 2, min(new_offset_y, (self.camera_board_size[1]) // 2))

        new_offset   = (new_offset_x, new_offset_y)

        self.Update_offset(new_offset)
        self.drag_first_pos = self.drag_second_pos


    def Set_h_scrollbar(self):
        self.main_window.Board_H_ScrollBar.blockSignals(True)
        self.main_window.Board_H_ScrollBar.setRange(  -(self.camera_board_size[0]) // 2,
                                                       (self.camera_board_size[0]) // 2)
        self.main_window.Board_H_ScrollBar.setPageStep((self.camera_board_size[0]) // 15)
        self.main_window.Board_H_ScrollBar.setValue(self.camera_offset[0])
        self.main_window.Board_H_ScrollBar.blockSignals(False)

    def Set_v_scrollbar(self):
        self.main_window.Board_V_ScrollBar.blockSignals(True)
        self.main_window.Board_V_ScrollBar.setRange(  -(self.camera_board_size[1]) // 2,
                                                       (self.camera_board_size[1]) // 2)
        self.main_window.Board_V_ScrollBar.setPageStep((self.camera_board_size[1]) // 15)
        self.main_window.Board_V_ScrollBar.setValue(self.camera_offset[1])
        self.main_window.Board_V_ScrollBar.blockSignals(False)

    def Update_layer_widget_list(self):
        for layer_widget in self.main_window.Layer_List_ScrollArea.findChildren(Layer_Widget):
            self.main_window.Layer_List_ScrollArea_Layout.removeWidget(layer_widget)
            layer_widget.deleteLater()
            sip.delete(layer_widget)

        spacer = self.main_window.Layer_List_ScrollArea_Layout.itemAt(0)
        if spacer:
            self.main_window.Layer_List_ScrollArea_Layout.removeItem(spacer)
            sip.delete(spacer)

        for layer in self.board_layer_controller.Get_layer_list():
            layer.Set_widget(self.Yield_layer_widget())
            layer.Set_selected_state_enum('unselected')
            self.main_window.Layer_List_ScrollArea_Layout.addWidget(layer.Get_widget())

        for layer in self.board_layer_controller.Get_selected_layer_list()[1:]:
            layer.Set_selected_state_enum('weak_selected')

        if len(self.board_layer_controller.Get_selected_layer_list()) > 0:
            self.main_window.Layer_Name_LineEdit.setEnabled(True)
            self.main_window.Mix_Mod_ComboBox.setEnabled(True)
            self.main_window.Opacity_Slider.setEnabled(True)

            strong_selected_layer = self.board_layer_controller.Get_selected_layer_list()[0]
            strong_selected_layer.Set_selected_state_enum('strong_selected')
            if strong_selected_layer.Get_layer_type_enum() == 'bit_layer':
                self.main_window.Func_Folder_StackedWidget.setCurrentIndex(0)
                self.tool_view.On_pencil_tool_button_clicked()
            elif strong_selected_layer.Get_layer_type_enum() == 'vector_layer':
                self.main_window.Func_Folder_StackedWidget.setCurrentIndex(1)
                self.tool_view.On_square_tool_button_clicked()

            self.main_window.Layer_Name_LineEdit.setText(strong_selected_layer.Get_name())
            mod_index = self.main_window.Mix_Mod_ComboBox.findText(strong_selected_layer.Get_mod_enum())
            self.main_window.Mix_Mod_ComboBox.setCurrentIndex(mod_index)
            self.main_window.Opacity_Slider.Set_current_value(strong_selected_layer.Get_opacity())
            self.main_window.Opacity_Slider.Set_right_text(f'{strong_selected_layer.Get_opacity()}%')
        else:
            self.main_window.Layer_Name_LineEdit.setEnabled(False)
            self.main_window.Mix_Mod_ComboBox.setEnabled(False)
            self.main_window.Opacity_Slider.setEnabled(False)

        spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_window.Layer_List_ScrollArea_Layout.addItem(spacer)

    def Yield_layer_widget(self):
        return Layer_Widget(self.main_window.Layer_List_ScrollArea_Widget)


    def On_Board_h_scrollbar_value_changed(self, value):
        self.Update_offset((value, self.camera_offset[1]))

    def On_Board_v_scrollbar_value_changed(self, value):
        self.Update_offset((self.camera_offset[0], value))

    def On_layer_name_lineedit_text_changed(self, text):
        layer = self.board_layer_controller.Get_strong_selected_layer()
        if layer is None:
            self.Notify_Controller.Send_label_notify('未选中图层')
            return

        layer.Set_name(text)
        self.backup_controller.Add_backup()

    def On_mix_mod_combobox_text_changed(self, text):
        layer = self.board_layer_controller.Get_strong_selected_layer()
        if layer is None:
            self.Notify_Controller.Send_label_notify('未选中图层')
            return

        layer.Set_mod_enum(text)
        self.board_layer_controller.Draw_painting()
        self.backup_controller.Add_backup()

    def On_opacity_slider_value_change(self, value):
        layer = self.board_layer_controller.Get_strong_selected_layer()
        if layer is None:
            self.Notify_Controller.Send_label_notify('未选中图层')
            return

        layer.Set_opacity(value)
        self.main_window.Opacity_Slider.Set_right_text(f'{value}%')
        self.board_layer_controller.Draw_painting()
        self.backup_controller.Add_backup()


    def Board_label_resize_event(self):
        self.Print_image(self.board_image)

    def Wheel_Event(self, event):
        mouse_pos  = (event.position().x(), event.position().y())

        if event.angleDelta().y() > 0:
            self.Zoom_in(mouse_pos)
        else:
            self.Zoom_out(mouse_pos)

    def Mouse_press_event(self, event):
        label_pos = (event.pos().x(), event.pos().y())
        board_pos = self.Label_pos_to_board_pos(label_pos)

        if event.button() == Qt.MiddleButton:
            self.Rotate_board_by_mouse(label_pos, first_point_flag = True)

        elif self.main_window.Get_key_space_pressed_flag() and event.button() == Qt.LeftButton:
            self.Drag_board_by_mouse(label_pos, first_point_flag = True)

        else:
            self.tool_controller.Mouse_press_event(label_pos, board_pos, event)

    def Mouse_move_event(self, event):
        label_pos = (event.pos().x(), event.pos().y())
        board_pos = self.Label_pos_to_board_pos(label_pos)

        if event.buttons() == Qt.MiddleButton:
            self.Rotate_board_by_mouse(label_pos, first_point_flag = False)

        elif self.main_window.Get_key_space_pressed_flag() and event.buttons() == Qt.LeftButton:
            self.Drag_board_by_mouse(label_pos, first_point_flag = False)

        else:
            self.tool_controller.Mouse_move_event(label_pos, board_pos, event)

    def Mouse_release_event(self, event):
        label_pos = (event.pos().x(), event.pos().y())
        board_pos = self.Label_pos_to_board_pos(label_pos)

        if event.button() == Qt.MiddleButton:
            self.Rotate_board_by_mouse(label_pos, first_point_flag = False)

        elif self.main_window.Get_key_space_pressed_flag() and event.button() == Qt.LeftButton:
            self.Drag_board_by_mouse(label_pos, first_point_flag = False)

        else:
            self.tool_controller.Mouse_release_event(label_pos, board_pos, event)


class Board_Layer_Controller:
    class Promet_Layer_Command_Struct:
        def __init__(self):
            self.command_enum = None
            self.caller_enum  = None

            #其他数据在方法里添加

    class Vector_Layer_Command_Struct:
        # 和Promet_Layer_Command_Struct原理完全一致，但使用场景不用，所以单独开个类
        def __init__(self):
            self.command_enum = None

    class Selection_Vector_Struct:
        def __init__(self):
            self.type_enum  = None

    class Selection_Mask:
        def __init__(self, controller, type_enum, selection_vector):
            self.controller = controller

            self.type_enum  = type_enum
            self.mask_image = self.Draw_mask(selection_vector)

        def Draw_mask(self, selection_vector):
            mask_image = Image.new('1', self.controller.Get_board_size(), 0)

            if self.type_enum == 'rect':
                first_pos  = selection_vector.first_pos
                second_pos = selection_vector.second_pos
                ImageDraw.Draw(mask_image).rectangle((first_pos[0], first_pos[1], second_pos[0], second_pos[1]),
                                                      outline = 1, fill = 1)

            return mask_image


    class Layer_Interface:
        def __init__(self, controller, widget, offset = (0, 0), mod_enum = '正常', opacity = 100):
            self.layer_type_enum     = None   #由子类负责
            self.selected_state_enum = 'unselected'

            self.controller          = controller
            self.widget              = widget
            self.widget.init(self, self.controller.style_manage_controller)
            self.widget.Hide_Button.clicked.connect(self.On_hide_button_clicked)
            self.widget.Lock_Button.clicked.connect(self.On_lock_button_clicked)
            self.widget.Move_Up_Button.clicked.connect(self.On_move_up_button_clicked)
            self.widget.Move_Down_Button.clicked.connect(self.On_move_down_button_clicked)
            self.widget.mouse_press_singal.connect(self.On_mouse_press_singal_emit)

            self.image     = None
            self.offset    = offset

            self.hide_flag = False
            self.lock_flag = False

            self.name      = None   #由子类负责
            self.mod_enum  = mod_enum
            self.opacity   = opacity

        def Draw_layer(self):
            # virtual function
            pass

        def Shift_layer(self, offset):
            self.offset = offset

        def Rotate_layer(self, angle):
            # virtual function
            pass

        def Zoom_layer(self, zoom):
            # virtual function
            pass


        def Set_preview_label(self):
            r, g, b, _ = self.controller._Get_highlight_back_color().getRgb()
            preview_background_image = Image.new('RGBA', self.widget.Get_preview_label_size(), (r, g, b, 255))

            preview_image = self.Draw_layer()
            preview_image_array = np.array(preview_image)
            preview_image_array[:, :, :3][preview_image_array[:, :, 3] == 0] = np.array([255, 255, 255])
            preview_image_array[:, :, 3] = np.array(255)
            preview_image = Image.fromarray(preview_image_array.astype('uint8'))

            if self.image.size[0] / preview_background_image.size[0] == self.image.size[1] / preview_background_image.size[1]:
                preview_image = preview_image.resize((preview_background_image.size[0], preview_background_image.size[1]))
                preview_background_image.paste(preview_image)
            elif self.image.size[0] / preview_background_image.size[0] > self.image.size[1] / preview_background_image.size[1]:
                preview_image = preview_image.resize((preview_background_image.size[0],
                                                round(preview_image.size[1] * preview_background_image.size[0] / preview_image.size[0])))
                preview_background_image.paste(preview_image, (0, (preview_background_image.size[1] - preview_image.size[1]) // 2))
            else:
                preview_image = preview_image.resize((round(preview_image.size[0] * preview_background_image.size[1] / preview_image.size[1]),
                                                            preview_background_image.size[1]))
                preview_background_image.paste(preview_image, ((preview_background_image.size[0] - preview_image.size[0]) // 2, 0))

            self.widget.Set_preview_label(preview_background_image)

        def Set_widget_info(self):
            self.widget.Set_widget_info()


        def On_hide_button_clicked(self):
            self.hide_flag = not self.hide_flag
            self.Set_widget_info()
            self.controller.Draw_painting()

        def On_lock_button_clicked(self):
            self.lock_flag = not self.lock_flag
            self.Set_widget_info()

        def On_move_up_button_clicked(self):
            self.controller.Move_up_layer(self)

        def On_move_down_button_clicked(self):
            self.controller.Move_down_layer(self)

        def On_mouse_press_singal_emit(self):
            self.controller.Change_layer_select_state(self)


        def Get_layer_size(self):
            # virtual function
            pass

        def Get_layer_type_enum(self):
            return self.layer_type_enum

        def Set_selected_state_enum(self, selected_state_enum):
            self.selected_state_enum = selected_state_enum
            self.Set_widget_info()

        def Set_widget(self, widget):
            self.widget = widget
            self.widget.init(self, self.controller.style_manage_controller)
            self.widget.Hide_Button.clicked.connect(self.On_hide_button_clicked)
            self.widget.Lock_Button.clicked.connect(self.On_lock_button_clicked)
            self.widget.Move_Up_Button.clicked.connect(self.On_move_up_button_clicked)
            self.widget.Move_Down_Button.clicked.connect(self.On_move_down_button_clicked)
            self.widget.mouse_press_singal.connect(self.On_mouse_press_singal_emit)
            self.Set_preview_label()
            self.Set_widget_info()

        def Get_widget(self):
            return self.widget

        def Get_offset(self):
            return self.offset

        def Get_hide_flag(self):
            return self.hide_flag

        def Get_lock_flag(self):
            return self.lock_flag

        def Get_name(self):
            return self.name

        def Set_name(self, name):
            self.name = name
            self.Set_widget_info()

        def Get_mod_enum(self):
            return self.mod_enum

        def Set_mod_enum(self, mod_enum):
            self.mod_enum = mod_enum
            self.Set_widget_info()

        def Get_opacity(self):
            return self.opacity

        def Set_opacity(self, opacity):
            self.opacity = opacity
            self.Set_widget_info()

    class Bit_Layer(Layer_Interface):
        next_bit_layer_index = 1

        def __init__(self, controller, widget, image = None, offset = (0, 0), name = '', mod_enum = '正常', opacity = 100):
            super().__init__(controller, widget, offset, mod_enum, opacity)
            self.layer_type_enum = 'bit_layer'

            self.image = image if image != None else Image.new('RGBA', self.controller.Get_board_size(), (0, 0, 0, 0))

            if name != '':
                self.name = name
            else:
                self.name = f'图层{controller.Bit_Layer.next_bit_layer_index}'
                controller.Bit_Layer.next_bit_layer_index += 1

            self.Set_preview_label()
            self.Set_widget_info()


        def Draw_layer(self):
            return self.image.copy()

        def Rotate_layer(self, angle):
            pass


        def Zoom_layer(self, zoom):
            pass

        def Get_layer_size(self):
            return self.image.size


        def Set_image(self, image):
            self.image = image.copy()
            self.Set_preview_label()

    class Vector_Layer(Layer_Interface):
        next_vector_layer_index = 1

        def __init__(self, controller, widget, image = None, offset = (0, 0), name = '', mod_enum = '正常', opacity = 100):
            super().__init__(controller, widget, offset, mod_enum, opacity)
            self.layer_type_enum = 'vector_layer'

            self.command_list   = []
            self.prompt_command = None
            self.image          = None

            self.rotate         = 0
            self.zoom           = (1, 1)
            self.layer_size     = (controller.Get_board_size()[0], controller.Get_board_size()[1])

            if name != '':
                self.name = name
            else:
                self.name = f'矢量图层{controller.Vector_Layer.next_vector_layer_index}'
                controller.Vector_Layer.next_vector_layer_index += 1

            self.Set_preview_label()
            self.Set_widget_info()

        def Draw_layer(self):
            board_size = self.controller.Get_board_size()
            image      = QImage(board_size[0], board_size[1], QImage.Format_ARGB32)
            image.fill(QColor(0, 0, 0, 0))
            painter    = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)

            transform = QTransform()
            transform.translate(-board_size[0] // 2, -board_size[1] // 2)
            transform.rotate(self.rotate)
            transform.translate(board_size[0] // 2,   board_size[1] // 2)
            transform.scale(self.zoom[0], self.zoom[1])
            painter.setTransform(transform)

            for command in (self.command_list + [self.prompt_command]) if self.prompt_command != None else self.command_list:
                if command.outline_color != None:
                    pen = QPen(QColor(command.outline_color))
                    pen.setWidth(command.outline_width)
                    painter.setPen(pen)
                else:
                    painter.setPen(Qt.NoPen)

                if command.fill_color != None:
                    brush = QBrush(QColor(command.fill_color))
                    painter.setBrush(brush)
                else:
                    painter.setBrush(Qt.NoBrush)

                if command.command_enum == 'rect':
                    painter.drawRoundedRect(command.x, command.y, command.width, command.height, command.x_radius, command.y_radius)

                elif command.command_enum == 'circle':
                    painter.drawEllipse(command.x, command.y, command.radius, command.radius)

                elif command.command_enum == 'ellipse':
                    painter.drawEllipse(command.x, command.y, command.x_radius, command.y_radius)

                elif command.command_enum == 'line':
                    painter.drawLine(command.first_pos[0], command.first_pos[1], command.second_pos[0], command.second_pos[1])

                elif command.command_enum == 'polygon':
                    point_list = []
                    for pos in command.pos_list:
                        point_list.append(QPoint(pos[0], pos[1]))

                    painter.drawPolygon(point_list, len(point_list))

                elif command.command_enum == 'polyline':
                    point_list = []
                    for pos in command.pos_list:
                        point_list.append(QPoint(pos[0], pos[1]))

                    painter.drawPolyline(point_list, len(point_list))

                elif command.command_enum == 'path':
                    path = QPainterPath()
                    for path_command in command.path_command_list:
                        if path_command.command_enum == 'M':
                            path.moveTo(*path_command.pos)
                        elif path_command.command_enum == 'L':
                            path.lineTo(*path_command.pos)
                        elif path_command.command_enum == 'C':
                            path.cubicTo(path_command.pos[0][0], path_command.pos[0][1],
                                         path_command.pos[1][0], path_command.pos[1][1],
                                         path_command.pos[2][0], path_command.pos[2][1])

                    painter.drawPath(path)

                elif command.command_enum == 'path_with_dot':
                    point_list = list(map(lambda point_pos: QPoint(point_pos[0], point_pos[1]), command.point_list))

                    pen = QPen(QColor(255, 0, 0))
                    pen.setWidth(5)
                    painter.setPen(pen)
                    painter.drawPoints(*point_list)

                    if command.outline_color != None:
                        pen = QPen(QColor(command.outline_color))
                        pen.setWidth(command.outline_width)
                        painter.setPen(pen)
                    else:
                        painter.setPen(Qt.NoPen)

                    path = QPainterPath()
                    for path_command in command.path_command_list:
                        if path_command.command_enum == 'M':
                            path.moveTo(*path_command.pos)
                        elif path_command.command_enum == 'L':
                            path.lineTo(*path_command.pos)
                        elif path_command.command_enum == 'C':
                            path.cubicTo(path_command.pos[0][0], path_command.pos[0][1],
                                         path_command.pos[1][0], path_command.pos[1][1],
                                         path_command.pos[2][0], path_command.pos[2][1])

                    painter.drawPath(path)


            painter.end()
            vector_image = ImageQt.fromqimage(image)

            if self.layer_size == board_size and self.offset == (0, 0):
                self.image      = vector_image.copy()
            else:
                bonding_box     = vector_image.getbbox()
                self.layer_size = vector_image.size
                self.image      = vector_image.crop(bonding_box)
                self.offset     = (bonding_box[0], bonding_box[1])

            return vector_image

        def Rotate_layer(self, angle):
            pass

        def Zoom_layer(self, zoom):
            pass


        def Get_layer_size(self):
            return self.layer_size


        def Set_command_list(self, command_list):
            self.command_list = command_list
            self.Set_preview_label()
            self.Draw_layer()

        def Set_prompt_command(self, command):
            self.prompt_command = command
            self.Draw_layer()

        def Formaliz_prompt_command(self):
            if self.prompt_command is not None:
                self.command_list.append(copy.copy(self.prompt_command))
                self.prompt_command = None
                self.Set_preview_label()
                self.Draw_layer()

    def __init__(self, main_window):
        self.main_window = main_window

        self.board_size           = (256, 256)
        self.current_frame        = None
        self.selection_mask       = None
        self.promet_layer_command = None

        self.painting             = Image.new('RGBA', self.board_size, (255, 255, 255, 0))
        self.base_layer           = Image.new('RGBA', self.board_size, (255, 255, 255, 0))
        self.background_layer     = Image.new('RGBA', self.board_size, (255, 255, 255, 255))

    def init(self):
        self.current_frame        = None
        self.selection_mask       = None
        self.promet_layer_command = None


    def Genrate_painting(self):
        painting_array = np.array(self.base_layer.copy(), dtype = 'int32')

        for layer in self.Get_layer_list()[::-1]:
            if not layer.Get_hide_flag():
                layer_image   = layer.Draw_layer()
                layer_offset  = layer.Get_offset()
                layer_opacity = layer.Get_opacity()

                temp_image    = Image.new('RGBA', self.board_size, (0, 0, 0, 0))
                temp_image.paste(layer_image, layer_offset, mask = layer_image)
                layer_image_array   = np.array(temp_image,  dtype = 'int32')
                layer_rgb           = layer_image_array[:, :, :3]
                painting_array_copy = painting_array.copy()
                painting_rgb        = painting_array_copy[:, :, :3]

                alpha_array         = painting_array[:, :, 3] + layer_image_array[:, :, 3]
                alpha_array[alpha_array > 0] = 255
                opaque_array        = np.zeros((self.board_size[0], self.board_size[1] ,3))

                if layer.mod_enum == '正常':
                    mask_array = layer_image_array[:, :, 3] == 255
                    painting_rgb[mask_array] = layer_rgb[mask_array]

                    opaque_array = painting_rgb.copy()

                elif layer.mod_enum == '正片叠底':
                    painting_rgb[painting_array_copy[:, :, 3] == 0] = np.array([255, 255, 255])
                    layer_rgb[layer_image_array[:, :, 3] == 0]      = np.array([255, 255, 255])

                    opaque_array = painting_rgb * layer_rgb / 255

                elif layer.mod_enum == '滤色':
                    painting_rgb[painting_array_copy[:, :, 3] == 0] = np.array([0, 0, 0])
                    layer_rgb[layer_image_array[:, :, 3] == 0]      = np.array([0, 0, 0])

                    opaque_array = 255 - (255 - painting_rgb) * (255 - layer_rgb) / 255

                elif layer.mod_enum == '叠加':
                    multiply_painting_rgb = painting_rgb.copy()
                    multiply_layer_rgb    = layer_rgb.copy()
                    multiply_painting_rgb[painting_array_copy[:, :, 3] == 0] = np.array([255, 255, 255])
                    multiply_layer_rgb[layer_image_array[:, :, 3] == 0]      = np.array([255, 255, 255])

                    multiply_opaque_array = opaque_array.copy()
                    multiply_opaque_array[:, :, :3] = multiply_painting_rgb * multiply_layer_rgb / 255

                    filter_painting_rgb = painting_rgb.copy()
                    filter_layer_rgb    = layer_rgb.copy()
                    filter_painting_rgb[painting_array_copy[:, :, 3] == 0] = np.array([0, 0, 0])
                    filter_layer_rgb[layer_image_array[:, :, 3] == 0]      = np.array([0, 0, 0])

                    filter_opaque_array = opaque_array.copy()
                    filter_opaque_array[:, :, :3] = 255 - (255 - filter_painting_rgb) * (255 - filter_layer_rgb) / 255

                    mask_array           = painting_rgb <= 128
                    temp_mask_array      = mask_array[:, :, 0] & mask_array[:, :, 1] & mask_array[:, :, 2]
                    mask_array[:, :, 0] &= temp_mask_array
                    mask_array[:, :, 1] &= temp_mask_array
                    mask_array[:, :, 2] &= temp_mask_array

                    opaque_array[ mask_array] = multiply_opaque_array[:, :, :3][ mask_array]
                    opaque_array[~mask_array] = filter_opaque_array[:, :, :3][~mask_array]

                elif layer.mod_enum == '颜色加深':
                    painting_rgb[painting_array_copy[:, :, 3] == 0] = np.array([255, 255, 255])
                    layer_rgb[layer_image_array[:, :, 3] == 0]      = np.array([0, 0, 0])

                    opaque_array[:, :, :3] = painting_rgb - \
                                             np.divide((255 - painting_rgb) * (255 - layer_rgb),
                                                        layer_rgb,
                                                        out = np.zeros_like(painting_rgb),
                                                        casting = 'unsafe',
                                                        where = layer_rgb != 0)
                    mask_array = ((layer_image_array[:, :, 3] == 255) & (painting_array_copy[:, :, 3] == 0))
                    opaque_array[mask_array] = layer_rgb[mask_array]

                elif layer.mod_enum == '颜色减淡':
                    painting_rgb[painting_array_copy[:, :, 3] == 0] = np.array([255, 255, 255])
                    layer_rgb[layer_image_array[:, :, 3] == 0] = np.array([0, 0, 0])

                    opaque_array[:, :, :3] = painting_rgb + \
                                             np.divide(painting_rgb * layer_rgb,
                                                       255 - layer_rgb,
                                                       out = np.zeros_like(painting_rgb),
                                                       casting = 'unsafe',
                                                       where = (255 - painting_rgb) != 0)
                    mask_array = ((layer_image_array[:, :, 3] == 255) & (painting_array_copy[:, :, 3] == 0))
                    opaque_array[mask_array] = layer_rgb[mask_array]

                elif layer.mod_enum == '线性加深':
                    painting_rgb[painting_array_copy[:, :, 3] == 0] = np.array([255, 255, 255])
                    layer_rgb[layer_image_array[:, :, 3] == 0]      = np.array([255, 255, 255])

                    opaque_array = painting_rgb + layer_rgb - 255

                elif layer.mod_enum == '变亮':
                    painting_rgb[painting_array_copy[:, :, 3] == 0] = np.array([0, 0, 0])
                    layer_rgb[layer_image_array[:, :, 3] == 0]      = np.array([0, 0, 0])

                    opaque_array = np.maximum(painting_rgb, layer_rgb)

                elif layer.mod_enum == '变暗':
                    painting_rgb[painting_array_copy[:, :, 3] == 0] = np.array([255, 255, 255])
                    layer_rgb[layer_image_array[:, :, 3] == 0]      = np.array([255, 255, 255])

                    opaque_array = np.minimum(painting_rgb, layer_rgb)

                elif layer.mod_enum == '柔光':
                    pass

                elif layer.mod_enum == '强光':
                    pass

                elif layer.mod_enum == '亮光':
                    pass

                elif layer.mod_enum == '点光':
                    pass

                elif layer.mod_enum == '线性光':
                    pass

                elif layer.mod_enum == '实色混合':
                    pass


                opaque_array = np.clip(opaque_array[:, :, :3], 0, 255)
                painting_array[:, :, :3] = (layer_opacity * opaque_array + (100 - layer_opacity) * painting_array[:, :, :3]) / 100
                painting_array[:, :,  3] = alpha_array


        painting = Image.fromarray(painting_array.astype('uint8'))
        background_layer = self.background_layer.copy()
        background_layer.paste(painting, mask = painting)
        return background_layer

    def Draw_painting(self):
        painting = self.Genrate_painting()

        self.painting = painting.copy()
        self.board_layer_view.Print_image(painting)

    def Draw_painting_new_project(self):
        self.current_frame = self.frame_controller.Get_current_frame()
        self.selection_mask       = None
        self.promet_layer_command = None

        painting = self.Genrate_painting()

        self.painting = painting.copy()
        self.board_layer_view.Print_image_new_project(painting)
        self.board_layer_view.Update_layer_widget_list()
        self.backup_controller.Add_backup()

    def Draw_painting_frame_change(self):
        self.current_frame = self.frame_controller.Get_current_frame()
        self.selection_mask       = None
        self.promet_layer_command = None

        painting = self.Genrate_painting()

        self.painting = painting.copy()
        self.board_layer_view.Print_image(painting)
        self.board_layer_view.Update_layer_widget_list()


    def Prompt_selection(self, selection_vector):
        if selection_vector.type_enum == 'rect_selection':
            self.promet_layer_command = Board_Layer_Controller.Promet_Layer_Command_Struct()
            self.promet_layer_command.command_enum = 'draw_rect_solid_line'
            self.promet_layer_command.caller_enum  = 'prompt_selection'
            self.promet_layer_command.first_pos    = selection_vector.first_pos
            self.promet_layer_command.second_pos   = selection_vector.second_pos

            self.board_layer_view.Print_image(self.painting)

    def Create_selection(self, selection_vector):
        if selection_vector.type_enum == 'rect_selection':
            self.promet_layer_command = Board_Layer_Controller.Promet_Layer_Command_Struct()
            self.promet_layer_command.command_enum = 'draw_rect_dotted_line'
            self.promet_layer_command.caller_enum  = 'create_selection'
            self.promet_layer_command.first_pos    = selection_vector.first_pos
            self.promet_layer_command.second_pos   = selection_vector.second_pos

            self.board_layer_view.Print_image(self.painting)

            self.selection_mask = Board_Layer_Controller.Selection_Mask(self, 'rect', selection_vector)

    def Cancel_selection(self):
        self.selection_mask = None

        if (self.promet_layer_command != None) and self.promet_layer_command.caller_enum == 'create_selection':
            self.Clear_promet_layer_command()

    def Copy_selection(self):
        if self.selection_mask is None:
            self.notify_controller.Send_label_notify('未建立选区')
            return

        selected_layer = self.Get_strong_selected_layer()
        if selected_layer == False:
            self.notify_controller.Send_label_notify('未选中图层')
            return
        if selected_layer.Get_layer_type_enum() != 'bit_layer':
            self.notify_controller.Send_label_notify('该工具暂时只支持对位图操作')
            return
        if selected_layer.Get_lock_flag():
            self.notify_controller.Send_label_notify('该图层已锁定')
            return

        layer_image  = selected_layer.Draw_layer()
        layer_offset = selected_layer.Get_offset()
        board_size   = self.board_size

        image = Image.new('RGBA', board_size, (0, 0, 0, 0))
        image.paste(layer_image, layer_offset)
        mask = self.selection_mask.mask_image.convert('L')
        mask = ImageOps.invert(mask)
        blank_image = Image.new('RGBA', board_size, (0, 0, 0, 0))
        image.paste(blank_image, mask = mask)

        bonding_box = image.getbbox()
        if bonding_box is None:
            self.notify_controller.Send_label_notify('选定的区域内没有像素')
            return
        image = image.crop(bonding_box)
        offset = (bonding_box[0], bonding_box[1])

        new_layer = Board_Layer_Controller.Bit_Layer(controller = self, widget = self.board_layer_view.Yield_layer_widget(), image = image, offset = offset)
        self.Insert_layer_and_select(new_layer, self.Get_strong_selected_layer_index())

        self.board_layer_view.Update_layer_widget_list()
        self.Cancel_selection()
        self.Draw_painting()
        self.backup_controller.Add_backup()

    def Cut_selection(self):
        if self.selection_mask is None:
            self.notify_controller.Send_label_notify('未建立选区')
            return
        selected_layer = self.Get_strong_selected_layer()
        if selected_layer == False:
            self.notify_controller.Send_label_notify('未选中图层')
            return
        if selected_layer.Get_layer_type_enum() != 'bit_layer':
            self.notify_controller.Send_label_notify('该工具暂时只支持对位图操作')
            return
        if selected_layer.Get_lock_flag():
            self.notify_controller.Send_label_notify('该图层已锁定')
            return

        layer_image  = selected_layer.Draw_layer()
        layer_offset = selected_layer.Get_offset()
        layer_size   = selected_layer.Get_layer_size()
        board_size   = self.board_size

        image = Image.new('RGBA', board_size, (0, 0, 0, 0))
        image.paste(layer_image, layer_offset)
        mask = self.selection_mask.mask_image.convert('L')
        mask = ImageOps.invert(mask)
        blank_image = Image.new('RGBA', board_size, (0, 0, 0, 0))
        image.paste(blank_image, mask = mask)

        bonding_box = image.getbbox()
        if bonding_box is None:
            self.notify_controller.Send_label_notify('选定的区域内没有像素')
            return
        image = image.crop(bonding_box)
        offset = (bonding_box[0], bonding_box[1])

        new_layer = Board_Layer_Controller.Bit_Layer(controller = self, widget = self.board_layer_view.Yield_layer_widget(), image = image, offset = offset)
        self.Insert_layer_and_select(new_layer, self.Get_strong_selected_layer_index())


        left   = 0 if layer_offset[0] >= 0 else layer_offset[0]
        top    = 0 if layer_offset[1] >= 0 else layer_offset[1]
        right  = board_size[0] if layer_offset[0] + layer_size[0] <= board_size[0] else layer_offset[0] + layer_size[0]
        button = board_size[1] if layer_offset[1] + layer_size[1] <= board_size[1] else layer_offset[1] + layer_size[1]

        layer_base_image = Image.new('RGBA', (right - left, button - top), (0, 0, 0, 0))
        layer_base_image.paste(layer_image, (layer_offset[0] if layer_offset[0] >= 0 else 0, layer_offset[1] if layer_offset[1] >= 0 else 0))
        mask_image = Image.new('1', (right - left, button - top), 0)
        mask_image.paste(self.selection_mask.mask_image, (-left, -top))

        blank_image = Image.new('RGBA', self.board_size, (0, 0, 0, 0))
        layer_base_image.paste(blank_image, mask = mask_image)

        if layer_size == board_size and layer_offset == (0, 0):
            selected_layer.Set_image(layer_base_image)
        else:
            bonding_box = layer_base_image.getbbox()
            if bonding_box is None:
                self.Delete_layer(selected_layer)
            else:
                selected_layer.Set_image(layer_base_image.crop(bonding_box))
                selected_layer.Shift_layer((bonding_box[0], bonding_box[1]))


        self.board_layer_view.Update_layer_widget_list()
        self.Cancel_selection()
        self.Draw_painting()
        self.backup_controller.Add_backup()

    def Clear_selection(self):
        if self.selection_mask is None:
            self.notify_controller.Send_label_notify('未建立选区')
            return
        selected_layer = self.Get_strong_selected_layer()
        if selected_layer == False:
            self.notify_controller.Send_label_notify('未选中图层')
            return
        if selected_layer.Get_layer_type_enum() != 'bit_layer':
            self.notify_controller.Send_label_notify('该工具暂时只支持对位图操作')
            return
        if selected_layer.Get_lock_flag():
            self.notify_controller.Send_label_notify('该图层已锁定')
            return

        layer_image  = selected_layer.Draw_layer()
        layer_offset = selected_layer.Get_offset()
        layer_size   = selected_layer.Get_layer_size()
        board_size   = self.board_size

        left   = 0 if layer_offset[0] >= 0 else layer_offset[0]
        top    = 0 if layer_offset[1] >= 0 else layer_offset[1]
        right  = board_size[0] if layer_offset[0] + layer_size[0] <= board_size[0] else layer_offset[0] + layer_size[0]
        button = board_size[1] if layer_offset[1] + layer_size[1] <= board_size[1] else layer_offset[1] + layer_size[1]

        layer_base_image = Image.new('RGBA', (right - left, button - top), (0, 0, 0, 0))
        layer_base_image.paste(layer_image, (layer_offset[0] if layer_offset[0] >= 0 else 0, layer_offset[1] if layer_offset[1] >= 0 else 0))
        mask_image = Image.new('1', (right - left, button - top), 0)
        mask_image.paste(self.selection_mask.mask_image, (-left, -top))

        blank_image = Image.new('RGBA', self.board_size, (0, 0, 0, 0))
        layer_base_image.paste(blank_image, mask = mask_image)

        if layer_size == board_size and layer_offset == (0, 0):
            selected_layer.Set_image(layer_base_image)
        else:
            bonding_box = layer_base_image.getbbox()
            if bonding_box is None:
                self.Delete_layer(selected_layer)
            else:
                selected_layer.Set_image(layer_base_image.crop(bonding_box))
                selected_layer.Shift_layer((bonding_box[0], bonding_box[1]))

        self.board_layer_view.Update_layer_widget_list()
        self.Cancel_selection()
        self.Draw_painting()
        self.backup_controller.Add_backup()


    def Yield_bit_layer(self):
        return Board_Layer_Controller.Bit_Layer(self, self.board_layer_view.Yield_layer_widget())

    def Add_bit_layer(self):
        new_layer = Board_Layer_Controller.Bit_Layer(self, self.board_layer_view.Yield_layer_widget())

        strong_selected_layer_index = self.Get_strong_selected_layer_index()
        if strong_selected_layer_index != None:
            self.Insert_layer_and_select(new_layer, strong_selected_layer_index)
        else:
            self.Insert_layer_and_select(new_layer, 0)
        self.board_layer_view.Update_layer_widget_list()
        self.backup_controller.Add_backup()

    def Add_vector_layer(self):
        new_layer = Board_Layer_Controller.Vector_Layer(self, self.board_layer_view.Yield_layer_widget())

        strong_selected_layer_index = self.Get_strong_selected_layer_index()
        if strong_selected_layer_index != None:
            self.Insert_layer_and_select(new_layer, strong_selected_layer_index)
        else:
            self.Insert_layer_and_select(new_layer, 0)
        self.board_layer_view.Update_layer_widget_list()
        self.backup_controller.Add_backup()

    def Change_layer_select_state(self, layer):
        selected_layer_index_list = self.Get_selected_layer_index_list()
        layer_index = self.Get_layer_list().index(layer)

        if self.main_window.Get_key_ctrl_pressed_flag():
            if layer_index in selected_layer_index_list:
                selected_layer_index_list.remove(layer_index)
            else:
                selected_layer_index_list.append(layer_index)
        else:
            selected_layer_index_list = [layer_index]

        self.Set_selected_layer(selected_layer_index_list)
        self.board_layer_view.Update_layer_widget_list()

    def Move_up_layer(self, layer):
        self.current_frame.Move_up_layer(layer)
        self.board_layer_view.Update_layer_widget_list()
        self.backup_controller.Add_backup()

    def Move_down_layer(self, layer):
        self.current_frame.Move_down_layer(layer)
        self.board_layer_view.Update_layer_widget_list()
        self.backup_controller.Add_backup()


    def Insert_layer(self, layer, index = None):
        self.current_frame.Insert_layer(layer) if index is None else self.current_frame.Insert_layer(layer, index)

    def Insert_layer_and_select(self, layer, index = None):
        self.current_frame.Insert_layer_and_select(layer) if index is None else self.current_frame.Insert_layer_and_select(layer, index)

    def Delete_layer(self, layer):
        self.current_frame.Delete_layer(layer)

    def Get_layer_list(self):
        return self.current_frame.Get_layer_list()

    def Get_strong_selected_layer(self):
        return self.current_frame.Get_strong_selected_layer()

    def Get_strong_selected_layer_index(self):
        return self.current_frame.Get_strong_selected_layer_index()

    def Get_selected_layer_list(self):
        return self.current_frame.Get_selected_layer_list()

    def Get_selected_layer_index_list(self):
        return self.current_frame.Get_selected_layer_index_list()

    def Set_selected_layer(self, index_list):
         self.current_frame.Set_selected_layer(index_list)


    def Get_board_size(self):
        return self.board_size

    def Set_board_size(self, board_size):
        self.board_size = board_size

        self.painting             = Image.new('RGBA', self.board_size, (255, 255, 255, 0))
        self.base_layer           = Image.new('RGBA', self.board_size, (255, 255, 255, 0))
        self.background_layer     = Image.new('RGBA', self.board_size, (255, 255, 255, 255))

    def Get_promet_layer_command(self):
        return self.promet_layer_command

    def Clear_promet_layer_command(self):
        if self.promet_layer_command != None:
            self.promet_layer_command = None
            self.board_layer_view.Print_image(self.painting)


    def _Get_highlight_back_color(self):
        return self.style_manage_controller.Get_highlight_back_color()


class Tool_View:
    def __init__(self, main_window):
        self.main_window = main_window

        self.checkable_button_list = []

    def init(self):
        self.checkable_button_list = [self.main_window.Pencil_Tool_Button,          self.main_window.Eraser_Tool_Button,
                                      self.main_window.Paintbrush_Tool_Button,      self.main_window.Fill_Tool_Button,

                                      self.main_window.Square_Tool_Button,          self.main_window.Rect_Tool_Button,
                                      self.main_window.Circle_Tool_Button,          self.main_window.Ellipse_Tool_Button,
                                      self.main_window.Polygon_Tool_Button,         self.main_window.Line_Tool_Button,
                                      self.main_window.Polyline_Tool_Button,        self.main_window.Path_Tool_Button,

                                      self.main_window.Zoom_Tool_Button,            self.main_window.Rotate_Tool_Button,
                                      self.main_window.Dragger_Tool_Button,         self.main_window.Pick_Color_Tool_Button,
                                      self.main_window.Rect_Selection_Tool_Button,  self.main_window.Free_Selection_Tool_Button,
                                      self.main_window.Magic_Selection_Tool_Button, self.main_window.Move_Layer_Tool_Button,]


    def On_pencil_tool_button_clicked(self):
        self.tool_controller.Select_pencil_tool()

        self.main_window.Func_Option_StackedWidget.setCurrentIndex(self.main_window.Func_Option_StackedWidget.indexOf(self.main_window.Pencil_Tool_Option_Page))
        for button in self.checkable_button_list:
            button.setChecked(False)

        self.main_window.Pencil_Tool_Button.setChecked(True)

    def On_eraser_tool_button_clicked(self):
        self.tool_controller.Select_eraser_tool()

        self.main_window.Func_Option_StackedWidget.setCurrentIndex(self.main_window.Func_Option_StackedWidget.indexOf(self.main_window.Eraser_Tool_Option_Page))
        for button in self.checkable_button_list:
            button.setChecked(False)

        self.main_window.Eraser_Tool_Button.setChecked(True)

    def On_paintbrush_tool_button_clicked(self):
        self.tool_controller.Select_paintbrush_tool()

        self.main_window.Func_Option_StackedWidget.setCurrentIndex(self.main_window.Func_Option_StackedWidget.indexOf(self.main_window.Paintbrush_Tool_Option_Page))
        for button in self.checkable_button_list:
            button.setChecked(False)

        self.main_window.Paintbrush_Tool_Button.setChecked(True)

    def On_fill_tool_button_clicked(self):
        self.tool_controller.Select_fill_tool()

        self.main_window.Func_Option_StackedWidget.setCurrentIndex(self.main_window.Func_Option_StackedWidget.indexOf(self.main_window.Fill_Tool_Option_Page))
        for button in self.checkable_button_list:
            button.setChecked(False)

        self.main_window.Fill_Tool_Button.setChecked(True)


    def On_square_tool_button_clicked(self):
        self.tool_controller.Select_square_tool()

        self.main_window.Func_Option_StackedWidget.setCurrentIndex(self.main_window.Func_Option_StackedWidget.indexOf(self.main_window.Square_Tool_Option_Page))
        for button in self.checkable_button_list:
            button.setChecked(False)

        self.main_window.Square_Tool_Button.setChecked(True)

    def On_path_tool_button_clicked(self):
        self.tool_controller.Select_path_tool()

        self.main_window.Func_Option_StackedWidget.setCurrentIndex(self.main_window.Func_Option_StackedWidget.indexOf(self.main_window.Path_Tool_Option_Page))
        for button in self.checkable_button_list:
            button.setChecked(False)

        self.main_window.Path_Tool_Button.setChecked(True)


    def On_rect_selection_button_clicked(self):
        self.tool_controller.Select_rect_selection_tool()

        self.main_window.Func_Option_StackedWidget.setCurrentIndex(self.main_window.Func_Option_StackedWidget.indexOf(self.main_window.Rect_Selection_Option_Page))
        for button in self.checkable_button_list:
            button.setChecked(False)

        self.main_window.Rect_Selection_Tool_Button.setChecked(True)


    def On_pencil_size_combobox_text_changed(self, text):
        range_dict = {1:(1,100), 5:(1,500), 10:(10,1000), 50:(50,5000)}
        mutlip_time = eval(re.findall('×(\d*)', text)[0])
        self.main_window.Pencil_Size_Slider.Set_left_text(f'×{mutlip_time}')
        self.main_window.Pencil_Size_Slider.Set_min_value(range_dict[mutlip_time][0])
        self.main_window.Pencil_Size_Slider.Set_max_value(range_dict[mutlip_time][1])
        self.main_window.Pencil_Size_Slider.Set_right_text(str(self.main_window.Pencil_Size_Slider.Get_current_value()))
        self.tool_controller._Set_pencil_tool_brush_size(self.main_window.Pencil_Size_Slider.Get_current_value())

    def On_pencil_size_slider_value_changed(self, value):
        self.tool_controller._Set_pencil_tool_brush_size(value)
        self.main_window.Pencil_Size_Slider.Set_right_text(f'{value}')

    def On_eraser_size_combobox_text_changed(self, text):
        range_dict = {1:(1,100), 5:(1,500), 10:(10,1000), 50:(50,5000)}
        mutlip_time = eval(re.findall('×(\d*)', text)[0])
        self.main_window.Eraser_Size_Slider.Set_left_text(f'×{mutlip_time}')
        self.main_window.Eraser_Size_Slider.Set_min_value(range_dict[mutlip_time][0])
        self.main_window.Eraser_Size_Slider.Set_max_value(range_dict[mutlip_time][1])
        self.main_window.Eraser_Size_Slider.Set_right_text(str(self.main_window.Eraser_Size_Slider.Get_current_value()))
        self.tool_controller._Set_eraser_tool_brush_size(self.main_window.Eraser_Size_Slider.Get_current_value())

    def On_eraser_size_slider_value_changed(self, value):
        self.tool_controller._Set_eraser_tool_brush_size(value)
        self.main_window.Eraser_Size_Slider.Set_right_text(f'{value}')

    def On_paintbrush_size_combobox_text_changed(self, text):
        range_dict = {1:(1,100), 5:(1,500), 10:(10,1000), 50:(50,5000)}
        mutlip_time = eval(re.findall('×(\d*)', text)[0])
        self.main_window.Paintbrush_Size_Slider.Set_left_text(f'×{mutlip_time}')
        self.main_window.Paintbrush_Size_Slider.Set_min_value(range_dict[mutlip_time][0])
        self.main_window.Paintbrush_Size_Slider.Set_max_value(range_dict[mutlip_time][1])
        self.main_window.Paintbrush_Size_Slider.Set_right_text(str(self.main_window.Paintbrush_Size_Slider.Get_current_value()))
        self.tool_controller._Set_paintbrush_tool_brush_size(self.main_window.Paintbrush_Size_Slider.Get_current_value())

    def On_paintbrush_size_slider_value_changed(self, value):
        self.tool_controller._Set_paintbrush_tool_brush_size(value)
        self.main_window.Paintbrush_Size_Slider.Set_right_text(f'{value}')

    def On_deepen_radio_button_clicked(self):
        self.tool_controller._Set_paintbrush_tool_brush_type('加深')

    def On_fade_radio_button_clicked(self):
        self.tool_controller._Set_paintbrush_tool_brush_type('减淡')

    def On_fill_tolerance_slider_value_changed(self, value):
        self.tool_controller._Set_fill_tool_tolerance(value)
        self.main_window.Fill_Tolerance_Slider.Set_right_text(f'{value}')

    def On_filling_radio_button_clicked(self):
        self.tool_controller._Set_fill_tool_fill_type_enum('抠图')

    def On_cutout_radio_button_clicked(self):
        self.tool_controller._Set_fill_tool_fill_type_enum('抠图')


    def On_square_outline_color_none_radio_button_clicked(self):
        self.tool_controller._Set_square_tool_outline_color(None)

    def On_square_outline_color_radio_button_clicked(self):
        self.tool_controller._Set_square_tool_outline_color(self.main_window.Square_Outline_Color_Indicator_Label.Get_color())

    def On_square_outline_color_indicator_label_update_color(self):
        self.main_window.Square_Outline_Color_Indicator_Label.Set_color(self.color_controller.Get_front_color())
        if self.main_window.Square_Outline_Color_Radio_Button.isChecked():
            self.tool_controller._Set_square_tool_outline_color(self.main_window.Square_Outline_Color_Indicator_Label.Get_color())

    def On_square_outline_width_slider_value_changed(self, value):
        self.tool_controller._Set_square_tool_outline_width(value)
        self.main_window.Square_Outline_Width_Slider.Set_right_text(f'{value}')

    def On_square_fill_color_none_radio_button_clicked(self):
        self.tool_controller._Set_square_tool_fill_color(None)

    def On_square_fill_color_radio_button_clicked(self):
        self.tool_controller._Set_square_tool_fill_color(self.main_window.Square_Fill_Color_Indicator_Label.Get_color())

    def On_square_fill_color_indicator_label_update_color(self):
        self.main_window.Square_Fill_Color_Indicator_Label.Set_color(self.color_controller.Get_front_color())
        if self.main_window.Square_Fill_Color_Radio_Button.isChecked():
            self.tool_controller._Set_square_tool_fill_color(self.main_window.Square_Fill_Color_Indicator_Label.Get_color())

    def On_square_x_radius_slider_lineEdit_text_changed(self, text):
        if not text.isdigit():
            self.main_window.Square_X_Radius_Slider_LineEdit.setText('0')
            value = 0
        else:
            if text.startswith('0'):
                text = text.lstrip('0')
                self.main_window.Square_X_Radius_Slider_LineEdit.setText('0' if len(text) == 0 else text)
                value = 0 if len(text) == 0 else eval(text)
            else:
                value = eval(text)
                if value > 100:
                    self.main_window.Square_X_Radius_Slider_LineEdit.setText('100')
                    value = 100

        self.tool_controller._Set_square_x_radius(value)
        self.main_window.Square_X_Radius_Slider.Set_current_value(value)
        self.main_window.Square_X_Radius_Slider.Set_right_text(f'{value}')

    def On_square_y_radius_slider_lineEdit_text_changed(self, text):
        if not text.isdigit():
            self.main_window.Square_Y_Radius_Slider_LineEdit.setText('0')
            value = 0
        else:
            if text.startswith('0'):
                text = text.lstrip('0')
                self.main_window.Square_Y_Radius_Slider_LineEdit.setText('0' if len(text) == 0 else text)
                value = 0 if len(text) == 0 else eval(text)
            else:
                value = eval(text)
                if value > 100:
                    self.main_window.Square_Y_Radius_Slider_LineEdit.setText('100')
                    value = 100

        self.tool_controller._Set_square_y_radius(value)
        self.main_window.Square_Y_Radius_Slider.Set_current_value(value)
        self.main_window.Square_Y_Radius_Slider.Set_right_text(f'{value}')

    def On_square_x_radius_slider_value_changed(self, value):
        self.tool_controller._Set_square_x_radius(value)
        self.main_window.Square_X_Radius_Slider.Set_right_text(f'{value}')
        self.main_window.Square_X_Radius_Slider_LineEdit.setText(str(value))

    def On_square_y_radius_slider_value_changed(self, value):
        self.tool_controller._Set_square_y_radius(value)
        self.main_window.Square_Y_Radius_Slider.Set_right_text(f'{value}')
        self.main_window.Square_Y_Radius_Slider_LineEdit.setText(str(value))


    def On_copy_selection_button_clicked(self):
        self.board_layer_controller.Copy_selection()

    def On_cut_selection_button_clicked(self):
        self.board_layer_controller.Cut_selection()

    def On_clear_selection_button_clicked(self):
        self.board_layer_controller.Clear_selection()

    def On_cancel_selection_button_clicked(self):
        self.board_layer_controller.Cancel_selection()


class Tool_Controller:
    class Tool_Interface:
        def __init__(self, controller):
            self.controller = controller

        def Constructor(self):
            #victual function
            pass

        def Destructor(self):
            #victual function
            pass

        def Mouse_press_event(self):
            #victual function
            pass

        def Mouse_move_event(self):
            #victual function
            pass

        def Mouse_release_event(self):
            #victual function
            pass


    class Bit_Draw_Tool_Interface(Tool_Interface):
        def __init__(self, controller):
            super().__init__(controller)

            self.brush_size = 10

            self.first_pos  = None
            self.second_pos = None

        def Draw(self, board_pos):
            layer = self.controller._Get_strong_selected_layer()
            if layer == False:
                self.controller._Send_label_notify('未选中图层')
                return
            if layer.Get_layer_type_enum() != 'bit_layer':
                self.controller._Send_label_notify('该工具只支持对位图图层操作')
                return
            if layer.Get_hide_flag():
                self.controller._Send_label_notify('该图层已隐藏')
                return
            if layer.Get_lock_flag():
                self.controller._Send_label_notify('该图层已锁定')
                return

            self.controller._Set_image_edited()

            board_size   = self.controller._Get_board_size()
            layer_size   = layer.Get_layer_size()
            layer_offset = layer.Get_offset()

            left   = 0 if layer_offset[0] >= 0 else layer_offset[0]
            top    = 0 if layer_offset[1] >= 0 else layer_offset[1]
            right  = board_size[0] if layer_offset[0] + layer_size[0] <= board_size[0] else layer_offset[0] + layer_size[0]
            button = board_size[1] if layer_offset[1] + layer_size[1] <= board_size[1] else layer_offset[1] + layer_size[1]

            painting_layer_size = (right - left, button - top)
            layer_pos           = (board_pos[0] - left, board_pos[1] - top)

            layer_image_array   = self.Yield_layer_image_array(layer.Draw_layer(), painting_layer_size, layer_offset)
            painting_mask_array = self.Yield_painting_mask_array(layer_pos, painting_layer_size)
            layer_image_array   = self.Process_painting(layer_image_array, painting_mask_array)
            layer_image         = Image.fromarray(layer_image_array)

            if layer_size == board_size and layer_offset == (0, 0):
                layer.Set_image(layer_image)
            else:
                bonding_box = layer_image.getbbox()
                layer.Set_image(layer_image.crop(bonding_box))
                layer.Shift_layer((bonding_box[0], bonding_box[1]))

            layer.Set_preview_label()
            self.controller._Draw_painting()

        def Yield_layer_image_array(self, layer_image, painting_layer_size, layer_offset):
            painting_image = Image.new('RGBA', painting_layer_size, (0, 0, 0, 0))
            painting_image.paste(layer_image, (layer_offset[0] if layer_offset[0] >= 0 else 0, layer_offset[1] if layer_offset[1] >= 0 else 0))
            layer_image_array = np.array(painting_image)

            return layer_image_array

        def Yield_painting_mask_array(self, layer_pos, mask_size):
            radius              = self.brush_size // 2
            painting_mask_array = np.zeros(mask_size[::-1], dtype = 'bool')

            if self.first_pos is None:
                self.first_pos = layer_pos

                y_array, x_array = np.ogrid[:mask_size[1], :mask_size[0]]
                dist_from_center = np.sqrt((x_array - layer_pos[0]) ** 2 + (y_array - layer_pos[1]) ** 2)

                painting_mask_array[dist_from_center <= radius] = True
            else:
                self.second_pos = layer_pos

                step_count = round(((self.second_pos[0] - self.first_pos[0]) ** 2 + (self.second_pos[1] - self.first_pos[1]) ** 2) ** 0.5 * 1.2)
                i_array    = np.round(np.linspace(self.first_pos[0], self.second_pos[0], step_count))
                j_array    = np.round(np.linspace(self.first_pos[1], self.second_pos[1], step_count))

                y_array, x_array = np.ogrid[:mask_size[1], :mask_size[0]]
                for i,j in zip(i_array, j_array):
                    dist_from_center = np.sqrt((x_array - i) ** 2 + (y_array - j) ** 2)
                    painting_mask_array[dist_from_center <= radius] = True

                self.first_pos = self.second_pos

            return painting_mask_array


        def Process_painting(self, layer_image_array, painting_area_array):
            #virtual function
            pass

        def Set_brush_size(self, value):
            self.brush_size = value


        def Constructor(self):
            self.first_pos  = None
            self.second_pos = None

        def Destructor(self):
            self.first_pos  = None
            self.second_pos = None

        def Mouse_press_event(self, board_pos, event):
            if event.button() == Qt.LeftButton:
                board_size = self.controller._Get_board_size()

                if 0 <= board_pos[0] < board_size[0] and 0 <= board_pos[1] < board_size[1]:
                    self.Draw(board_pos)
                else:
                    self.first_pos  = None
                    self.second_pos = None

        def Mouse_move_event(self, board_pos, event):
            if event.buttons() == Qt.LeftButton:
                board_size = self.controller._Get_board_size()

                if 0 <= board_pos[0] < board_size[0] and 0 <= board_pos[1] < board_size[1]:
                    self.Draw(board_pos)
                else:
                    self.first_pos  = None
                    self.second_pos = None

        def Mouse_release_event(self, board_pos, event):
            if event.button() == Qt.LeftButton:
                self.controller._Add_backup()

            self.first_pos  = None
            self.second_pos = None

    class Pencil_Tool(Bit_Draw_Tool_Interface):
        def __init__(self, controller):
            super().__init__(controller)

        def Process_painting(self, layer_image_array, painting_mask_array):
            r, g, b, _ = self.controller._Get_front_color().getRgb()
            color_array = np.array((r, g, b, 255))

            layer_image_array[painting_mask_array] = color_array
            return layer_image_array

    class Eraser_Tool(Bit_Draw_Tool_Interface):
        def __init__(self, controller):
            super().__init__(controller)

        def Process_painting(self, layer_image_array, painting_mask_array):
            color_array = np.array((0, 0, 0, 0))

            layer_image_array[painting_mask_array] = color_array
            return layer_image_array

    class Paintbrush_Tool(Bit_Draw_Tool_Interface):
        def __init__(self, controller):
            super().__init__(controller)

            self.brush_type_enum              = '加深'
            self.paintbrush_layer_image_array = None
            self.unpainted_mask_array         = None

        def Set_brush_type_enum(self, type_enum):
            self.brush_type_enum = type_enum


        def Constructor(self):
            super().Constructor()

            self.paintbrush_layer_image_array = None
            self.unpainted_mask_array         = None

        def Destructor(self):
            super().Destructor()

            self.paintbrush_layer_image_array = None
            self.unpainted_mask_array         = None

        def Yield_layer_image_array(self, layer_image, painting_layer_size, layer_offset):
            if self.unpainted_mask_array is None:
                layer_image_array                 = super().Yield_layer_image_array(layer_image, painting_layer_size, layer_offset)
                self.paintbrush_layer_image_array = layer_image_array.astype('int32')
                self.unpainted_mask_array         = np.ones(layer_image.size[::-1], dtype = 'bool')

            return self.paintbrush_layer_image_array

        def Process_painting(self, layer_image_array, painting_mask_array):
            r, g, b, _ = self.controller._Get_front_color().getRgb()
            color_array = np.array((r, g, b, 0))

            if self.brush_type_enum == '加深':
                self.paintbrush_layer_image_array[painting_mask_array & self.unpainted_mask_array] += color_array
                self.paintbrush_layer_image_array[painting_mask_array & self.unpainted_mask_array] += np.array((0, 0, 0, 255))

                self.unpainted_mask_array[painting_mask_array] = False

            elif self.brush_type_enum == '减淡':
                self.paintbrush_layer_image_array[painting_mask_array & self.unpainted_mask_array] -= color_array
                self.paintbrush_layer_image_array[painting_mask_array & self.unpainted_mask_array] += np.array((0, 0, 0, 255))

                self.unpainted_mask_array[painting_mask_array] = False

            self.paintbrush_layer_image_array = np.clip(self.paintbrush_layer_image_array, 0, 255)
            layer_image_array = self.paintbrush_layer_image_array.copy()
            layer_image_array = layer_image_array.astype('uint8')

            return layer_image_array

        def Mouse_press_event(self, board_pos, event):
            self.paintbrush_layer_image_array = None
            self.unpainted_mask_array         = None
            super().Mouse_press_event(board_pos, event)

        def Mouse_release_event(self, board_pos, event):
            super().Mouse_release_event(board_pos, event)

            self.paintbrush_layer_image_array = None
            self.unpainted_mask_array         = None

    class Fill_Tool(Tool_Interface):
        def __init__(self, controller):
            self.controller     = controller

            self.tolerance      = 0
            self.fill_type_enum = '填充'

        def Set_tolerance(self, value):
            self.tolerance = value

        def Set_fill_type_enum(self, fill_type_enum):
            self.fill_type_enum = fill_type_enum


        def Fill_layer(self, board_pos):
            layer = self.controller._Get_strong_selected_layer()
            if layer == False:
                self.controller._Send_label_notify('未选中图层')
                return
            if layer.Get_layer_type_enum() != 'bit_layer':
                self.controller._Send_label_notify('该工具只支持对位图图层操作')
                return
            if layer.Get_hide_flag():
                self.controller._Send_label_notify('该图层已隐藏')
                return
            if layer.Get_lock_flag():
                self.controller._Send_label_notify('该图层已锁定')
                return

            self.controller._Set_image_edited()

            board_size   = self.controller._Get_board_size()
            layer_size   = layer.Get_layer_size()
            layer_offset = layer.Get_offset()

            left   = 0 if layer_offset[0] >= 0 else layer_offset[0]
            top    = 0 if layer_offset[1] >= 0 else layer_offset[1]
            right  = board_size[0] if layer_offset[0] + layer_size[0] <= board_size[0] else layer_offset[0] + layer_size[0]
            button = board_size[1] if layer_offset[1] + layer_size[1] <= board_size[1] else layer_offset[1] + layer_size[1]

            layer_pos = (board_pos[0] - left, board_pos[1] - top)

            layer_image = Image.new('RGBA', (right - left, button - top), (0, 0, 0, 0))
            layer_image.paste(layer.Draw_layer(), (layer_offset[0] if layer_offset[0] >= 0 else 0, layer_offset[1] if layer_offset[1] >= 0 else 0))

            if self.fill_type_enum == '填充':
                r, g, b, _ = self.controller._Get_front_color().getRgb()
                ImageDraw.floodfill(image = layer_image, xy = board_pos, value = (r, g, b, 255), thresh = self.tolerance + 1)
            elif self.fill_type_enum == '抠图':
                ImageDraw.floodfill(image = layer_image, xy = board_pos, value = (0, 0, 0, 0),   thresh = self.tolerance + 1)

            if layer_size == board_size and layer_offset == (0, 0):
                layer.Set_image(layer_image)
            else:
                bonding_box = layer_image.getbbox()
                layer.Set_image(layer_image.crop(bonding_box))
                layer.Shift_layer((bonding_box[0], bonding_box[1]))

            layer.Set_preview_label()
            self.controller._Draw_painting()
            self.controller._Add_backup()


        def Mouse_press_event(self, board_pos, event):
            if event.button() == Qt.LeftButton:
                board_size = self.controller._Get_board_size()

                if 0 <= board_pos[0] < board_size[0] and 0 <= board_pos[1] < board_size[1]:
                    self.Fill_layer(board_pos)

        def Mouse_move_event(self, board_pos, event):
            pass

        def Mouse_release_event(self, board_pos, event):
            pass


    class Vector_Tool_Interface(Tool_Interface):
        def __init__(self, controller):
            super().__init__(controller)

            self.outline_color = QColor(0, 0, 0)
            self.outline_width = 2
            self.fill_color    = QColor(255, 255, 255)


        def Set_outline_color(self, color):
            self.outline_color = QColor(color) if color is not None else None

        def Set_outline_width(self, value):
            self.outline_width = value

        def Set_fill_color(self, color):
            self.fill_color = QColor(color) if color is not None else None


        def Draw_prompt(self):
            #victual function
            pass

        def Formaliz_prompt_command(self):
            layer = self.controller._Get_strong_selected_layer()

            layer.Formaliz_prompt_command()
            layer.Set_preview_label()
            self.controller._Draw_painting()


        def Constructor(self):
            #victual function
            pass

        def Destructor(self):
            #victual function
            pass

        def Mouse_press_event(self):
            #victual function
            pass

        def Mouse_move_event(self):
            #victual function
            pass

        def Mouse_release_event(self):
            #victual function
            pass

    class Square_Tool(Vector_Tool_Interface):
        def __init__(self, controller):
            super().__init__(controller)

            self.first_pos  = None
            self.second_pos = None

            self.x_radius   = 0
            self.y_radius   = 0

        def Set_x_radius(self, value):
            self.x_radius = value

        def Set_y_radius(self, value):
            self.y_radius = value


        def Draw_prompt(self):
            layer = self.controller._Get_strong_selected_layer()
            if layer == False:
                self.controller._Send_label_notify('未选中图层')
                return
            if layer.Get_layer_type_enum() != 'vector_layer':
                self.controller._Send_label_notify('该工具只支持对矢量图层操作')
                return
            if layer.Get_hide_flag():
                self.controller._Send_label_notify('该图层已隐藏')
                return
            if layer.Get_lock_flag():
                self.controller._Send_label_notify('该图层已锁定')
                return
            layer_offset = layer.Get_offset()

            self.controller._Set_image_edited()

            square_command = Board_Layer_Controller.Vector_Layer_Command_Struct()
            square_command.command_enum = 'rect'

            square_command.outline_color = QColor(self.outline_color) if self.outline_color is not None else None
            square_command.outline_width = self.outline_width
            square_command.fill_color    = QColor(self.fill_color) if self.fill_color is not None else None

            length = min(abs(self.second_pos[0] - self.first_pos[0]), abs(self.second_pos[1] - self.first_pos[1]))
            square_command.x      = (self.first_pos[0] if self.first_pos[0] < self.second_pos[0] else self.first_pos[0] - length) - layer_offset[0]
            square_command.y      = (self.first_pos[1] if self.first_pos[1] < self.second_pos[1] else self.first_pos[1] - length) - layer_offset[1]
            square_command.width  = length
            square_command.height = length

            square_command.x_radius = self.x_radius
            square_command.y_radius = self.y_radius

            layer.Set_prompt_command(square_command)
            self.controller._Draw_painting()


        def Constructor(self):
            self.first_pos  = None
            self.second_pos = None

        def Destructor(self):
            self.first_pos  = None
            self.second_pos = None

        def Mouse_press_event(self, board_pos, event):
            if event.button() == Qt.LeftButton:
                board_size = self.controller._Get_board_size()
                board_pos  = (max(0, min(board_pos[0], board_size[0])),
                              max(0, min(board_pos[1], board_size[1])))
                self.first_pos  = board_pos
                self.second_pos = None

        def Mouse_move_event(self, board_pos, event):
            if event.buttons() == Qt.LeftButton:
                board_size = self.controller._Get_board_size()
                board_pos  = (max(0, min(board_pos[0], board_size[0])),
                              max(0, min(board_pos[1], board_size[1])))
                self.second_pos = board_pos
                self.Draw_prompt()

        def Mouse_release_event(self, board_pos, event):
            if event.button() == Qt.LeftButton:
                self.Formaliz_prompt_command()

                self.first_pos  = None
                self.second_pos = None

    class Path_Tool(Vector_Tool_Interface):
        def __init__(self, controller):
            super().__init__(controller)
            self.fill_color = None

            self.pos_list   = []


        def Draw_prompt(self):
            layer = self.controller._Get_strong_selected_layer()
            if layer == False:
                self.controller._Send_label_notify('未选中图层')
                return
            if layer.Get_layer_type_enum() != 'vector_layer':
                self.controller._Send_label_notify('该工具只支持对矢量图层操作')
                return
            if layer.Get_hide_flag():
                self.controller._Send_label_notify('该图层已隐藏')
                return
            if layer.Get_lock_flag():
                self.controller._Send_label_notify('该图层已锁定')
                return
            layer_offset = layer.Get_offset()

            self.controller._Set_image_edited()

            path_command = Board_Layer_Controller.Vector_Layer_Command_Struct()
            path_command.command_enum = 'path_with_dot'

            path_command.outline_color     = QColor(self.outline_color) if self.outline_color is not None else None
            path_command.outline_width     = self.outline_width
            path_command.fill_color        = None

            path_command.point_list        = copy.copy(self.pos_list)
            path_command.path_command_list = self.Parse_path(layer_offset)

            layer.Set_prompt_command(path_command)
            self.controller._Draw_painting()

        def Formaliz_prompt_command(self):
            if len(self.pos_list) == 0:
                return

            layer = self.controller._Get_strong_selected_layer()
            if layer == False:
                self.controller._Send_label_notify('未选中图层')
                return
            if layer.Get_layer_type_enum() != 'vector_layer':
                self.controller._Send_label_notify('该工具只支持对矢量图层操作')
                return
            if layer.Get_hide_flag():
                self.controller._Send_label_notify('该图层已隐藏')
                return
            if layer.Get_lock_flag():
                self.controller._Send_label_notify('该图层已锁定')
                return
            layer_offset = layer.Get_offset()

            self.controller._Set_image_edited()

            path_command = Board_Layer_Controller.Vector_Layer_Command_Struct()
            path_command.command_enum = 'path'

            path_command.outline_color     = QColor(self.outline_color) if self.outline_color is not None else None
            path_command.outline_width     = self.outline_width
            path_command.fill_color        = None

            path_command.path_command_list = self.Parse_path(layer_offset)

            layer.Set_prompt_command(path_command)
            layer.Formaliz_prompt_command()
            layer.Set_preview_label()
            self.controller._Draw_painting()


        def Parse_path(self, layer_offset):
            class Path_Command_Struct:
                pass

            path_command_list = []

            new_command = Path_Command_Struct()
            new_command.command_enum = 'M'
            new_command.pos = self.pos_list[0]
            path_command_list.append(copy.copy(new_command))

            if len(self.pos_list) == 1:
                return path_command_list

            elif len(self.pos_list) == 2:
                new_command = Path_Command_Struct()
                new_command.command_enum = 'L'
                new_command.pos = self.pos_list[1]
                path_command_list.append(copy.copy(new_command))
                return path_command_list

            else:
                for i in range(len(self.pos_list) - 1):
                    control_point_list = []

                    if i == 0:
                        control_point_list.append((self.pos_list[i    ][0], self.pos_list[i    ][1]))
                        control_point_list.append((self.pos_list[i    ][0], self.pos_list[i    ][1]))
                        control_point_list.append((self.pos_list[i + 1][0], self.pos_list[i + 1][1]))
                        control_point_list.append((self.pos_list[i + 2][0], self.pos_list[i + 2][1]))
                    elif i + 1 == len(self.pos_list) - 1:
                        control_point_list.append((self.pos_list[i - 1][0], self.pos_list[i - 1][1]))
                        control_point_list.append((self.pos_list[i    ][0], self.pos_list[i    ][1]))
                        control_point_list.append((self.pos_list[i + 1][0], self.pos_list[i + 1][1]))
                        control_point_list.append((self.pos_list[i + 1][0], self.pos_list[i + 1][1]))
                    else:
                        control_point_list.append((self.pos_list[i - 1][0], self.pos_list[i - 1][1]))
                        control_point_list.append((self.pos_list[i    ][0], self.pos_list[i    ][1]))
                        control_point_list.append((self.pos_list[i + 1][0], self.pos_list[i + 1][1]))
                        control_point_list.append((self.pos_list[i + 2][0], self.pos_list[i + 2][1]))

                    new_command = Path_Command_Struct()
                    new_command.command_enum = 'C'
                    new_command.pos = [((-control_point_list[0][0] + 6 * control_point_list[1][0] + control_point_list[2][0]) / 6, (-control_point_list[0][1] + 6 * control_point_list[1][1] + control_point_list[2][1]) / 6),
                                       (( control_point_list[1][0] + 6 * control_point_list[2][0] - control_point_list[3][0]) / 6, ( control_point_list[1][1] + 6 * control_point_list[2][1] - control_point_list[3][1]) / 6),
                                       (  control_point_list[2][0], control_point_list[2][1])]

                    path_command_list.append(copy.copy(new_command))

                return path_command_list


        def Constructor(self):
            self.pos_list   = []

        def Destructor(self):
            self.pos_list   = []

        def Mouse_press_event(self, board_pos, event):
            if event.button() == Qt.LeftButton:
                board_size = self.controller._Get_board_size()
                board_pos  = (max(0, min(board_pos[0], board_size[0])),
                              max(0, min(board_pos[1], board_size[1])))
                self.pos_list.append(board_pos)
                self.Draw_prompt()
            elif event.button() == Qt.RightButton:
                if len(self.pos_list) > 1:
                    self.pos_list.pop()
                    self.Draw_prompt()

        def Mouse_move_event(self, board_pos, event):
            pass

        def Mouse_release_event(self, board_pos, event):
            pass

        def Key_event(self, event):
            if event.key() == Qt.Key_Enter:
                self.Formaliz_prompt_command()
                self.pos_list = []


    class Rect_Selection_Tool(Tool_Interface):
        def __init__(self, controller):
            self.controller = controller

            self.first_pos        = None
            self.second_pos       = None


        def Constructor(self):
            self.first_pos  = None
            self.second_pos = None

        def Destructor(self):
            self.first_pos  = None
            self.second_pos = None


        def Prompt_selection_vector(self, board_pos):
            selection_vector                 = Board_Layer_Controller.Selection_Vector_Struct()
            selection_vector.type_enum       = 'rect_selection'
            selection_vector.first_pos  = self.first_pos
            selection_vector.second_pos = self.second_pos

            self.controller._Prompt_selection_vector(selection_vector)

        def Create_selection_vector(self, board_pos):
            selection_vector                 = Board_Layer_Controller.Selection_Vector_Struct()
            selection_vector.type_enum       = 'rect_selection'
            selection_vector.first_pos  = self.first_pos
            selection_vector.second_pos = self.second_pos

            self.controller._Create_selection_vector(selection_vector)


        def Mouse_press_event(self, board_pos, event):
            if event.button() == Qt.LeftButton:
                board_size = self.controller._Get_board_size()
                board_pos = (max(0, min(board_pos[0], board_size[0])),
                             max(0, min(board_pos[1], board_size[1])))
                self.first_pos        = board_pos
                self.second_pos       = None

        def Mouse_move_event(self, board_pos, event):
            if event.buttons() == Qt.LeftButton:
                board_size = self.controller._Get_board_size()
                board_pos = (max(0, min(board_pos[0], board_size[0])),
                             max(0, min(board_pos[1], board_size[1])))
                self.second_pos = board_pos
                self.Prompt_selection_vector(board_pos)

        def Mouse_release_event(self, board_pos, event):
            if event.button() == Qt.LeftButton:
                board_size = self.controller._Get_board_size()
                board_pos = (max(0, min(board_pos[0], board_size[0])),
                             max(0, min(board_pos[1], board_size[1])))
                self.second_pos = board_pos
                self.Create_selection_vector(board_pos)


    def __init__(self, main_window):
        self.main_window = main_window

        self.current_tool = None

        self.pencil_tool         = Tool_Controller.Pencil_Tool(self)
        self.eraser_tool         = Tool_Controller.Eraser_Tool(self)
        self.paintbrush_tool     = Tool_Controller.Paintbrush_Tool(self)
        self.fill_tool           = Tool_Controller.Fill_Tool(self)

        self.square_tool         = Tool_Controller.Square_Tool(self)
        self.path_tool           = Tool_Controller.Path_Tool(self)

        self.rect_selection_tool = Tool_Controller.Rect_Selection_Tool(self)

        self.board_pos_only_list = [self.pencil_tool, self.eraser_tool, self.paintbrush_tool, self.fill_tool,
                                    self.square_tool, self.path_tool,
                                    self.rect_selection_tool]
        self.label_pos_only_list = []
        self.both_pos_list       = []

        self.accept_key_event_list = [self.path_tool]

    def init(self):
        self.current_tool = self.pencil_tool
        self.current_tool.Constructor()


    def Mouse_press_event(self, label_pos, board_pos, event):
        if   self.current_tool in self.board_pos_only_list:
             self.current_tool.Mouse_press_event(board_pos, event)
        elif self.current_tool in self.label_pos_only_list:
             self.current_tool.Mouse_press_event(label_pos, event)
        elif self.current_tool in self.both_pos_list:
             self.current_tool.Mouse_press_event(label_pos, board_pos, event)

    def Mouse_move_event(self, label_pos, board_pos, event):
        if   self.current_tool in self.board_pos_only_list:
             self.current_tool.Mouse_move_event(board_pos, event)
        elif self.current_tool in self.label_pos_only_list:
             self.current_tool.Mouse_move_event(label_pos, event)
        elif self.current_tool in self.both_pos_list:
             self.current_tool.Mouse_move_event(label_pos, board_pos, event)

    def Mouse_release_event(self, label_pos, board_pos, event):
        if   self.current_tool in self.board_pos_only_list:
             self.current_tool.Mouse_release_event(board_pos, event)
        elif self.current_tool in self.label_pos_only_list:
             self.current_tool.Mouse_release_event(label_pos, event)
        elif self.current_tool in self.both_pos_list:
             self.current_tool.Mouse_release_event(label_pos, board_pos, event)

    def Ket_event(self, event):
        if self.current_tool in self.accept_key_event_list:
            self.current_tool.Key_event(event)


    def Select_pencil_tool(self):
        self.current_tool.Destructor()
        self.current_tool = self.pencil_tool
        self.current_tool.Constructor()

    def Select_eraser_tool(self):
        self.current_tool.Destructor()
        self.current_tool = self.eraser_tool
        self.current_tool.Constructor()

    def Select_paintbrush_tool(self):
        self.current_tool.Destructor()
        self.current_tool = self.paintbrush_tool
        self.current_tool.Constructor()

    def Select_fill_tool(self):
        self.current_tool.Destructor()
        self.current_tool = self.fill_tool
        self.current_tool.Constructor()


    def Select_square_tool(self):
        self.current_tool.Destructor()
        self.current_tool = self.square_tool
        self.current_tool.Constructor()

    def Select_path_tool(self):
        self.current_tool.Destructor()
        self.current_tool = self.path_tool
        self.current_tool.Constructor()


    def Select_rect_selection_tool(self):
        self.current_tool.Destructor()
        self.current_tool = self.rect_selection_tool
        self.current_tool.Constructor()


    def _Set_pencil_tool_brush_size(self, value):
        self.pencil_tool.Set_brush_size(value)

    def _Set_eraser_tool_brush_size(self, value):
        self.eraser_tool.Set_brush_size(value)

    def _Set_paintbrush_tool_brush_size(self, value):
        self.paintbrush_tool.Set_brush_size(value)

    def _Set_paintbrush_tool_brush_type(self, type_enum):
        self.paintbrush_tool.Set_brush_type_enum(type_enum)

    def _Set_fill_tool_tolerance(self, value):
        self.fill_tool.Set_tolerance(value)

    def _Set_fill_tool_fill_type_enum(self, fill_type_enum):
        self.fill_tool.Set_fill_type_enum(fill_type_enum)


    def _Set_square_tool_outline_color(self, color):
        self.square_tool.Set_outline_color(color)

    def _Set_square_tool_outline_width(self, value):
        self.square_tool.Set_outline_width(value)

    def _Set_square_tool_fill_color(self, color):
        self.square_tool.Set_fill_color(color)

    def _Set_square_x_radius(self, value):
        self.square_tool.Set_x_radius(value)

    def _Set_square_y_radius(self, value):
        self.square_tool.Set_y_radius(value)


    def _Draw_painting(self):
        self.board_layer_controller.Draw_painting()

    def _Prompt_selection_vector(self, selection_vector):
        self.board_layer_controller.Prompt_selection(selection_vector)

    def _Create_selection_vector(self, selection_vector):
        self.board_layer_controller.Create_selection(selection_vector)

    def _Get_board_size(self):
        return self.board_layer_controller.Get_board_size()

    def _Get_strong_selected_layer(self):
        return self.board_layer_controller.Get_strong_selected_layer()

    def _Get_front_color(self):
        return self.color_controller.Get_front_color()

    def _Get_back_color(self):
        return self.color_controller.Get_back_color()

    def _Send_label_notify(self, text):
        self.notify_controller.Send_label_notify(text)

    def _Add_backup(self):
        self.backup_controller.Add_backup()

    def _Set_image_edited(self):
        self.main_window.Set_image_edited_flag(True)


class Color_Controller:
    def __init__(self, main_window):
        self.main_window = main_window

        self.front_color = QColor(0, 0, 0)
        self.back_color  = QColor(255, 255, 255)

    def init(self):
        self.main_window.Color_Picker_Widget.color_change_singal.connect(self.On_color_change_singal_emit)
        self.main_window.Color_Indicator_Widget.switch_color_singal.connect(self.On_switch_color_singal_emit)

        self.main_window.Color_Picker_Widget.Set_current_color(self.front_color)
        self.main_window.Color_Indicator_Widget.Set_front_color(self.front_color)
        self.main_window.Color_Indicator_Widget.Set_back_color(self.back_color)


    def On_color_change_singal_emit(self, color):
        r, g, b, _ = color.getRgb()
        self.front_color.setRgb(r, g, b)
        self.main_window.Color_Indicator_Widget.Set_front_color(self.front_color)

    def On_switch_color_singal_emit(self):
        self.front_color, self.back_color = self.back_color, self.front_color

        self.main_window.Color_Picker_Widget.Set_current_color(self.front_color)
        self.main_window.Color_Indicator_Widget.Set_front_color(self.front_color)
        self.main_window.Color_Indicator_Widget.Set_back_color(self.back_color)


    def Get_front_color(self):
        return self.front_color

    def Set_front_color(self, color):
        r, g, b, _ = color.getRgb()
        self.front_color.setRgb(r, g, b)

        self.main_window.Color_Picker_Widget.Set_current_color(self.front_color)
        self.main_window.Color_Indicator_Widget.Set_front_color(self.front_color)

    def Get_back_color(self):
        return self.back_color

    def Set_back_color(self, color):
        r, g, b, _ = color.getRgb()
        self.back_color.setRgb(r, g, b)

        self.main_window.Color_Indicator_Widget.Set_back_color(self.back_color)


class Notify_Controller(QObject):
    release_label_notify_singal = pyqtSignal(str)

    def __init__(self, main_window):
        self.main_window = main_window
        super().__init__()

        self.label_notify_list = []
        self.label_notify_busy_flag = False
        self.label_notify_thread = Thread(target = self._Label_notify_thread_action, args = ())
        self.label_notify_thread.start()
        self.label_notify_timer = QTimer()
        self.label_notify_timer.timeout.connect(self._On_label_notify_timer_timeout)
        self.release_label_notify_singal.connect(self._Release_label_notify)

    def init(self):
        pass


    def Send_label_notify(self, text):
        self.label_notify_list.append({'text' : text, 'time' : time.time()})

    def _Label_notify_thread_action(self):
        while True:
            time.sleep(0.05)

            if len(self.label_notify_list) > 0 and not self.label_notify_busy_flag:
                label_notify = self.label_notify_list.pop(0)
                if label_notify['time'] - time.time() > 8:
                    pass
                else:
                    self.release_label_notify_singal.emit(label_notify['text'])

    def _Release_label_notify(self, text):
        self.main_window.Notify_Label.setText(text)
        self.label_notify_busy_flag = True
        self.label_notify_timer.start(2500)

    def _On_label_notify_timer_timeout(self):
        self.main_window.Notify_Label.setText('')
        self.label_notify_busy_flag = False


class Backup_Controller:
    class Snapshot_Backup_Struct:
        def __init__(self):
            self.frame_list          = []
            self.current_frame_index = None

    class Frame_Backup_Struct:
        def __init__(self):
            self.layer_list = []
            self.selected_layer_index_list = []

    class Layer_Backup_Struct:
        def __init__(self):
            self.layer_type_enum = None

            self.offset          = None

            self.name            = None
            self.hide_flag       = None
            self.lock_flag       = None
            self.mod_enum        = None
            self.opacity         = None

            self.image           = None

            self.command_list    = None
            self.rotate          = None
            self.zoom            = None

    def __init__(self, main_window):
        self.main_window  = main_window

        self.backup_list  = []
        self.backup_pin   = -1

        self.backup_limit = 30

    def init(self):
        pass

    def Yield_backup_snapshot(self):
        snapshot_backup = Backup_Controller.Snapshot_Backup_Struct()

        frame_list = self.frame_controller.Get_frame_list()
        current_frame = self.frame_controller.Get_current_frame()
        snapshot_backup.current_frame_index = frame_list.index(current_frame)

        for frame in frame_list:
            frame_backup = Backup_Controller.Frame_Backup_Struct()

            for layer in frame.Get_layer_list():
                layer_backup                      = Backup_Controller.Layer_Backup_Struct()
                layer_backup.layer_type_enum      = layer.layer_type_enum
                layer_backup.selected_state_enum  = layer.selected_state_enum
                layer_backup.offset               = layer.offset
                layer_backup.hide_flag            = layer.hide_flag
                layer_backup.lock_flag            = layer.lock_flag
                layer_backup.name                 = layer.name
                layer_backup.mod_enum             = layer.mod_enum
                layer_backup.opacity              = layer.opacity

                if layer_backup.layer_type_enum   == 'bit_layer':
                    layer_backup.image            = layer.image.copy()
                elif layer_backup.layer_type_enum == 'vector_layer':
                    layer_backup.command_list     = copy.deepcopy(layer.command_list)
                    layer_backup.rotate           = layer.rotate
                    layer_backup.zoom             = layer.zoom
                    layer_backup.layer_size       = layer.layer_size

                frame_backup.layer_list.append(layer_backup)

            frame_backup.selected_layer_index_list = frame.Get_selected_layer_index_list()
            snapshot_backup.frame_list.append(frame_backup)

        return snapshot_backup

    def Revert_backup_snapshot(self, snapshot):
        frame_list = []

        for frame_backup in snapshot.frame_list:
            frame = Frame_Controller.Frame(self.frame_controller)

            for layer_backup in frame_backup.layer_list:
                if layer_backup.layer_type_enum == 'bit_layer':
                    layer       = Board_Layer_Controller.Bit_Layer.__new__(Board_Layer_Controller.Bit_Layer)
                    layer.image = layer_backup.image.copy()
                elif layer_backup.layer_type_enum == 'vector_layer':
                    layer = Board_Layer_Controller.Vector_Layer.__new__(Board_Layer_Controller.Vector_Layer)
                    layer.command_list    = copy.deepcopy(layer_backup.command_list)
                    layer.rotate          = layer_backup.rotate
                    layer.zoom            = layer_backup.zoom
                    layer.layer_size      = layer_backup.layer_size

                layer.layer_type_enum     = layer_backup.layer_type_enum
                layer.selected_state_enum = layer_backup.selected_state_enum
                layer.controller          = self.board_layer_controller

                layer.offset              = layer_backup.offset
                layer.hide_flag           = layer_backup.hide_flag
                layer.lock_flag           = layer_backup.lock_flag
                layer.name                = layer_backup.name
                layer.mod_enum            = layer_backup.mod_enum
                layer.opacity             = layer_backup.opacity

                layer.widget              = self.board_layer_view.Yield_layer_widget()
                layer.widget.                         init(layer, self.style_manage_controller)
                layer.widget.Hide_Button.clicked.     connect(layer.On_hide_button_clicked)
                layer.widget.Lock_Button.clicked.     connect(layer.On_lock_button_clicked)
                layer.widget.Move_Up_Button.clicked.  connect(layer.On_move_up_button_clicked)
                layer.widget.Move_Down_Button.clicked.connect(layer.On_move_down_button_clicked)
                layer.widget.mouse_press_singal.      connect(layer.On_mouse_press_singal_emit)

                layer.Set_preview_label()
                layer.Set_widget_info()

                frame.Insert_layer(layer)

            frame.Set_selected_layer(frame_backup.selected_layer_index_list)
            frame_list.append(frame)

        self.frame_controller.Set_frame_list(frame_list)
        self.frame_controller.Set_current_frame(snapshot.current_frame_index)

        self.board_layer_controller.Draw_painting_frame_change()


    def Add_backup(self):
        if self.backup_pin != len(self.backup_list) - 1:
            while self.backup_pin != len(self.backup_list) - 1:
                self.backup_list.pop()

            self.backup_list.append(self.Yield_backup_snapshot())
            self.backup_pin += 1

        else:
            if len(self.backup_list) < self.backup_limit:
                self.backup_list.append(self.Yield_backup_snapshot())
                self.backup_pin += 1
            else:
                self.backup_list.pop(0)
                self.backup_list.append(self.Yield_backup_snapshot())

    def Revoke_backup(self):
        if self.backup_pin > 0:
            self.backup_pin -= 1
            self.Revert_backup_snapshot(self.backup_list[self.backup_pin])

        elif self.backup_pin == 0:
            self.notify_controller.Send_label_notify('已经是第一个备份了')

    def Redo_backup(self):
        if self.backup_pin != len(self.backup_list) - 1:
            self.backup_pin += 1
            self.Revert_backup_snapshot(self.backup_list[self.backup_pin])
        else:
           self.notify_controller.Send_label_notify('已经是最后一个备份了')


class Style_Manage_Controller:
    def __init__(self, main_window):
        self.main_window = main_window

        self.base_color            = QColor(240, 240, 240)
        self.board_color           = QColor(160 ,160, 160)
        self.text_color            = QColor(0, 0, 0)
        self.highlight_back_color  = QColor(176, 176, 176)
        self.highlight_front_color = QColor(255, 255, 255)
        self.weak_selected_color   = QColor(189, 242, 255)
        self.strong_selected_color = QColor(219, 219, 255)

    def init(self):
        pass


    def Get_base_color(self):
        return self.base_color

    def Set_base_color(self, color):
        r, g, b, _ = color.getRgb()
        self.base_color = QColor(r, g, b)

        palette = self.main_window.palette()
        palette.setColor(QPalette.Background, self.base_color)
        self.main_window.setPalette(palette)
        self.main_window.update()

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

    def Get_highlight_back_color(self):
        return self.highlight_back_color

    def Set_highlight_back_color(self, color):
        r, g, b, _ = color.getRgb()
        self.highlight_back_color = QColor(r, g, b)

    def Get_highlight_front_color(self):
        return self.highlight_front_color

    def Set_highlight_front_color(self, color):
        r, g, b, _ = color.getRgb()
        self.highlight_front_color = QColor(r, g, b)

    def Get_weak_selected_color(self):
        return self.weak_selected_color

    def Set_weak_selected_color(self, color):
        r, g, b, _ = color.getRgb()
        self.weak_selected_color = QColor(r, g, b)

    def Get_strong_selected_color(self):
        return self.strong_selected_color

    def Set_strong_selected_color(self, color):
        r, g, b, _ = color.getRgb()
        self.strong_selected_color = QColor(r, g, b)


class File_Project_Controller:
    def __init__(self, main_window):
        self.main_window = main_window

    def init(self):
        pass

    def New_project(self, board_size):
        self.board_layer_controller.Set_board_size(board_size)

        first_frame = Frame_Controller.Frame(self.frame_controller)
        first_frame.Insert_layer(self.board_layer_controller.Yield_bit_layer())
        first_frame.Set_selected_layer([0])
        frame_list = [first_frame]

        self.frame_controller.Set_frame_list(frame_list)
        self.board_layer_controller.Draw_painting_new_project()

    def Open_project(self):
        open_path = QFileDialog.getOpenFileName(self.main_window)[0]
        if len(open_path) == 0:
            return
        try:
            with open(open_path, encoding = 'utf-8') as file:
                save = json.loads(file.read())
                self.board_layer_controller.Set_board_size(tuple(save['board_size']))

                frame_list = []
                for frame_save in save['frame_save_list']:
                    frame = Frame_Controller.Frame(self.frame_controller)

                    for layer_save in frame_save:
                        if layer_save['layer_type_enum'] == 'bit_layer':
                            layer                 = Board_Layer_Controller.Bit_Layer.__new__(Board_Layer_Controller.Bit_Layer)
                            layer.layer_type_enum = layer_save['layer_type_enum']

                            base64_data  = bytes(layer_save['image'], encoding = "utf-8")
                            image_buffer = BytesIO(base64.b64decode(base64_data))
                            image        = Image.open(image_buffer)

                            layer.image  = image
                        elif layer_save['layer_type_enum'] == 'vector_layer':
                            layer = Board_Layer_Controller.Vector_Layer.__new__(Board_Layer_Controller.Vector_Layer)
                            layer.layer_type_enum = layer_save['layer_type_enum']
                            layer.rotate          = layer_save['rotate']
                            layer.zoom            = tuple(layer_save['zoom'])
                            layer.layer_size      = tuple(layer_save['layer_size'])
                            layer.prompt_command  = None

                            command_list = []
                            for command_save in layer_save['command_list']:
                                command                = Board_Layer_Controller.Vector_Layer_Command_Struct()
                                command.command_enum   = command_save['command_enum']
                                command.outline_color  = QColor(command_save['outline_color'][0], command_save['outline_color'][1], command_save['outline_color'][1]) if command_save['outline_color'] is not None else None
                                command.outline_width  = command_save['outline_width']
                                command.fill_color     = QColor(command_save['fill_color'][0],    command_save['fill_color'][1],    command_save['fill_color'][1])    if command_save['fill_color']    is not None else None

                                if command.command_enum   == 'rect':
                                    command.x          = command_save['x']
                                    command.y          = command_save['y']
                                    command.width      = command_save['width']
                                    command.height     = command_save['height']
                                    command.x_radius   = command_save['x_radius']
                                    command.y_radius   = command_save['y_radius']

                                elif command.command_enum == 'circle':
                                    command.x          = command_save['x']
                                    command.y          = command_save['y']
                                    command.radius     = command_save['radius']

                                elif command.command_enum == 'ellipse':
                                    command.x          = command_save['x']
                                    command.y          = command_save['y']
                                    command.x_radius   = command_save['x_radius']
                                    command.y_radius   = command_save['y_radius']

                                elif command.command_enum == 'line':
                                    command.first_pos  = tuple(command_save['first_pos'])
                                    command.second_pos = tuple(command_save['second_pos'])

                                elif command.command_enum == 'polygon':
                                    command.point_list = list(map(lambda pos_list : tuple(pos_list), command_save['point_list']))

                                elif command.command_enum == 'polyline':
                                    command.point_list = list(map(lambda pos_list : tuple(pos_list), command_save['point_list']))

                                elif command.command_enum == 'path':
                                    path_command_list  = []
                                    class Path_Command_Struct:
                                        pass

                                    for path_command_save in command_save['path_command_list']:
                                        path_command = Path_Command_Struct()
                                        path_command.command_enum = path_command_save['command_enum']

                                        if path_command.command_enum == 'M':
                                            path_command.pos = tuple(path_command_save['pos'])
                                        elif path_command.command_enum == 'C':
                                            path_command.pos = list(map(lambda pos_list : tuple(pos_list), path_command_save['pos']))

                                        path_command_list.append(path_command)

                                    command.path_command_list = path_command_list

                                command_list.append(command)

                            layer.command_list = command_list

                        layer.selected_state_enum = 'unselected'
                        layer.controller          = self.board_layer_controller

                        layer.offset              = tuple(layer_save['offset'])
                        layer.hide_flag           = False
                        layer.lock_flag           = False
                        layer.name                = layer_save['name']
                        layer.mod_enum            = layer_save['mod_enum']
                        layer.opacity             = layer_save['opacity']

                        layer.widget              = self.board_layer_view.Yield_layer_widget()
                        layer.widget.                         init(layer, self.style_manage_controller)
                        layer.widget.Hide_Button.clicked.     connect(layer.On_hide_button_clicked)
                        layer.widget.Lock_Button.clicked.     connect(layer.On_lock_button_clicked)
                        layer.widget.Move_Up_Button.clicked.  connect(layer.On_move_up_button_clicked)
                        layer.widget.Move_Down_Button.clicked.connect(layer.On_move_down_button_clicked)
                        layer.widget.mouse_press_singal.      connect(layer.On_mouse_press_singal_emit)

                        layer.Set_preview_label()
                        layer.Set_widget_info()

                        frame.Insert_layer(layer)
                    frame.Set_selected_layer([])
                    frame_list.append(frame)

                self.frame_controller.Set_frame_list(frame_list)
                self.frame_controller.Set_current_frame(0)

                self.board_layer_controller.Draw_painting_frame_change()

        except BaseException as e:
            self.notify_controller.Send_label_notify('文件已损坏，无法读取')
            return

    def Save_as_project(self, path):
        if path == None:
            saning_path = QFileDialog.getSaveFileName(self.main_window)[0]
            if len(saning_path) == 0:
                return
            if not saning_path.endswith('.easypaint'):
                saning_path += '.easypaint'

        save = {'board_size' : self.board_layer_controller.Get_board_size()}
        frame_save_list = []

        frame_list = self.frame_controller.Get_frame_list()
        for frame in frame_list:
            frame_save = []

            for layer in frame.Get_layer_list():
                layer_save = dict()
                layer_save['layer_type_enum'] = layer.layer_type_enum
                layer_save['offset']          = layer.offset
                layer_save['name']            = layer.name
                layer_save['mod_enum']        = layer.mod_enum
                layer_save['opacity']         = layer.opacity

                if layer.layer_type_enum     == 'bit_layer':
                    image_buffer = BytesIO()
                    layer.image.save(image_buffer, 'png')
                    layer_save['image'] = str(base64.b64encode(image_buffer.getvalue()), encoding = 'utf-8')

                elif layer.layer_type_enum == 'vector_layer':
                    layer_save['rotate']     = layer.rotate
                    layer_save['zoom']       = layer.zoom
                    layer_save['layer_size'] = layer.layer_size

                    command_list = []
                    for command in layer.command_list:
                        command_dict = dict()
                        command_dict['outline_color'] = command.outline_color.getRgb()[0:3] if command.outline_color != None else None
                        command_dict['outline_width'] = command.outline_width
                        command_dict['fill_color']    = command.fill_color.getRgb()[0:3] if command.fill_color != None else None

                        command_dict['command_enum']  = command.command_enum
                        if command.command_enum == 'rect':
                            command_dict['x']          = command.x
                            command_dict['y']          = command.y
                            command_dict['width']      = command.width
                            command_dict['height']     = command.height
                            command_dict['x_radius']   = command.x_radius
                            command_dict['y_radius']   = command.y_radius

                        elif command.command_enum == 'circle':
                            command_dict['x']          = command.x
                            command_dict['y']          = command.y
                            command_dict['radius']     = command.radius

                        elif command.command_enum == 'ellipse':
                            command_dict['x']          = command.x
                            command_dict['y']          = command.y
                            command_dict['x_radius']   = command.x_radius
                            command_dict['y_radius']   = command.y_radius

                        elif command.command_enum == 'line':
                            command_dict['first_pos']  = command.first_pos
                            command_dict['second_pos'] = command.second_pos

                        elif command.command_enum == 'polygon':
                            command_dict['point_list'] = command.point_list

                        elif command.command_enum == 'polyline':
                            command_dict['point_list'] = command.point_list

                        elif command.command_enum == 'path':
                            path_command_list = []

                            for path_command in command.path_command_list:
                                path_command_list.append({'command_enum' : path_command.command_enum,
                                                          'pos'          : path_command.pos})

                            command_dict['path_command_list'] = path_command_list

                        command_list.append(command_dict)

                    layer_save['command_list'] = command_list


                frame_save.append(layer_save)

            frame_save_list.append(frame_save)

        save['frame_save_list'] = frame_save_list
        with open(saning_path, 'w', encoding = 'utf-8') as file:
            file.write(json.dumps(save, ensure_ascii = False))


class Menu_Tab_Distributor:
    def __init__(self, main_window):
        self.main_window = main_window

    def init(self):
        pass


    def On_new_action_triggered(self):
        

    def On_open_action_triggered(self):
        self.file_project_controller.Open_project()

    def On_save_as_action_triggered(self):
        self.file_project_controller.Save_project(None)


    def On_revoke_action_triggered(self):
        self.backup_controller.Revoke_backup()

    def On_redo_action_triggered(self):
        self.backup_controller.Redo_backup()


    def On_new_bit_layer_action_triggered(self):
        self.board_layer_controller.Add_bit_layer()

    def On_new_vector_layer_action_triggered(self):
        self.board_layer_controller.Add_vector_layer()


    def On_cancel_selection_action_triggered(self):
        self.board_layer_controller.Cancel_selection()

    def On_copy_selection_action_triggered(self):
        self.board_layer_controller.Copy_selection()

    def On_cut_selection_action_triggered(self):
        self.board_layer_controller.Cut_selection()

    def On_clear_selection_action_triggered(self):
        self.board_layer_controller.Clear_selection()


    def On_normal_color_action_triggered(self):
        self.style_manage_controller.Set_base_color(QColor(240, 240, 240))

    def On_miku_color_action_triggered(self):
        self.style_manage_controller.Set_base_color(QColor(57, 197, 187))

    def On_bili_color_action_triggered(self):
        self.style_manage_controller.Set_base_color(QColor(249, 131, 151))

    def On_red_color_action_triggered(self):
        self.style_manage_controller.Set_base_color(QColor(243, 67, 52))

    def On_yellow_color_action_triggered(self):
        self.style_manage_controller.Set_base_color(QColor(253, 192, 5))

    def On_green_color_action_triggered(self):
        self.style_manage_controller.Set_base_color(QColor(138, 193, 74))

    def On_blue_color_action_triggered(self):
        self.style_manage_controller.Set_base_color(QColor(31, 148, 243))

    def On_purple_color_action_triggered(self):
        self.style_manage_controller.Set_base_color(QColor(154, 38, 175))

    def On_white_color_action_triggered(self):
        self.style_manage_controller.Set_base_color(QColor(255, 255, 255))

    def On_black_color_action_triggered(self):
        self.style_manage_controller.Set_base_color(QColor(0, 0, 0))


class Event_And_Singal_Distributor:
    def __init__(self, main_window):
        self.main_window = main_window

    def init(self):
        self.main_window.keyPressEvent                 = self.main_window.Main_window_key_press_event
        self.main_window.keyReleaseEvent               = self.main_window.Main_window_key_release_event


        self.main_window.Board_Label.wheelEvent        = self.board_layer_view.Wheel_Event
        self.main_window.Board_Label.mousePressEvent   = self.board_layer_view.Mouse_press_event
        self.main_window.Board_Label.mouseMoveEvent    = self.board_layer_view.Mouse_move_event
        self.main_window.Board_Label.mouseReleaseEvent = self.board_layer_view.Mouse_release_event
        self.main_window.Board_Label.resize_signal.connect(self.board_layer_view.Board_label_resize_event)

        self.main_window.Board_H_ScrollBar.valueChanged.connect(self.board_layer_view.On_Board_h_scrollbar_value_changed)
        self.main_window.Board_V_ScrollBar.valueChanged.connect(self.board_layer_view.On_Board_v_scrollbar_value_changed)


        self.main_window.Layer_Name_LineEdit.textChanged.    connect(self.board_layer_view.On_layer_name_lineedit_text_changed)
        self.main_window.Mix_Mod_ComboBox.currentTextChanged.connect(self.board_layer_view.On_mix_mod_combobox_text_changed)
        self.main_window.Opacity_Slider.value_change_single. connect(self.board_layer_view.On_opacity_slider_value_change)


        self.main_window.Pencil_Tool_Button.clicked.        connect(self.tool_view.On_pencil_tool_button_clicked)
        self.main_window.Eraser_Tool_Button.clicked.        connect(self.tool_view.On_eraser_tool_button_clicked)
        self.main_window.Paintbrush_Tool_Button.clicked.    connect(self.tool_view.On_paintbrush_tool_button_clicked)
        self.main_window.Fill_Tool_Button.clicked.          connect(self.tool_view.On_fill_tool_button_clicked)

        self.main_window.Square_Tool_Button.clicked.        connect(self.tool_view.On_square_tool_button_clicked)
        self.main_window.Path_Tool_Button.clicked.          connect(self.tool_view.On_path_tool_button_clicked)

        self.main_window.Rect_Selection_Tool_Button.clicked.connect(self.tool_view.On_rect_selection_button_clicked)


        self.main_window.Pencil_Size_ComboBox.currentTextChanged.    connect(self.tool_view.On_pencil_size_combobox_text_changed)
        self.main_window.Pencil_Size_Slider.value_change_single.     connect(self.tool_view.On_pencil_size_slider_value_changed)
        self.main_window.Eraser_Size_ComboBox.currentTextChanged.    connect(self.tool_view.On_eraser_size_combobox_text_changed)
        self.main_window.Eraser_Size_Slider.value_change_single.     connect(self.tool_view.On_eraser_size_slider_value_changed)
        self.main_window.Paintbrush_Size_ComboBox.currentTextChanged.connect(self.tool_view.On_paintbrush_size_combobox_text_changed)
        self.main_window.Paintbrush_Size_Slider.value_change_single. connect(self.tool_view.On_paintbrush_size_slider_value_changed)
        self.main_window.Deepen_Radio_Button.clicked.                connect(self.tool_view.On_deepen_radio_button_clicked)
        self.main_window.Fade_Radio_Button.clicked.                  connect(self.tool_view.On_fade_radio_button_clicked)
        self.main_window.Fill_Tolerance_Slider.value_change_single.  connect(self.tool_view.On_fill_tolerance_slider_value_changed)
        self.main_window.Cutout_Radio_Button.clicked.                connect(self.tool_view.On_cutout_radio_button_clicked)
        self.main_window.Filling_Radio_Button.clicked.               connect(self.tool_view.On_filling_radio_button_clicked)


        self.main_window.Square_Outline_Color_None_Radio_Button.clicked.          connect(self.tool_view.On_square_outline_color_none_radio_button_clicked)
        self.main_window.Square_Outline_Color_Radio_Button.clicked.               connect(self.tool_view.On_square_outline_color_radio_button_clicked)
        self.main_window.Square_Outline_Color_Indicator_Label.update_color_singal.connect(self.tool_view.On_square_outline_color_indicator_label_update_color)
        self.main_window.Square_Outline_Width_Slider.value_change_single.         connect(self.tool_view.On_square_outline_width_slider_value_changed)
        self.main_window.Square_Fill_Color_None_Radio_Button.clicked.             connect(self.tool_view.On_square_fill_color_none_radio_button_clicked)
        self.main_window.Square_Fill_Color_Radio_Button.clicked.                  connect(self.tool_view.On_square_fill_color_radio_button_clicked)
        self.main_window.Square_Fill_Color_Indicator_Label.update_color_singal.   connect(self.tool_view.On_square_fill_color_indicator_label_update_color)
        self.main_window.Square_X_Radius_Slider_LineEdit.textChanged.             connect(self.tool_view.On_square_x_radius_slider_lineEdit_text_changed)
        self.main_window.Square_Y_Radius_Slider_LineEdit.textChanged.             connect(self.tool_view.On_square_y_radius_slider_lineEdit_text_changed)
        self.main_window.Square_X_Radius_Slider.value_change_single.              connect(self.tool_view.On_square_x_radius_slider_value_changed)
        self.main_window.Square_Y_Radius_Slider.value_change_single.              connect(self.tool_view.On_square_y_radius_slider_value_changed)


        self.main_window.Copy_Selection_Button.clicked.  connect(self.tool_view.On_copy_selection_button_clicked)
        self.main_window.Cut_Selection_Button.clicked.   connect(self.tool_view.On_cut_selection_button_clicked)
        self.main_window.Clear_Selection_Button.clicked. connect(self.tool_view.On_clear_selection_button_clicked)
        self.main_window.Cancel_Selection_Button.clicked.connect(self.tool_view.On_cancel_selection_button_clicked)


        self.main_window.New_Action.triggered.             connect(self.menu_tab_distributor.On_new_action_triggered)
        self.main_window.Open_Action.triggered.            connect(self.menu_tab_distributor.On_open_action_triggered)
        self.main_window.Save_As_Action.triggered.         connect(self.menu_tab_distributor.On_save_as_action_triggered)
        self.main_window.Revoke_Action.triggered.          connect(self.menu_tab_distributor.On_revoke_action_triggered)
        self.main_window.Redo_Action.triggered.            connect(self.menu_tab_distributor.On_redo_action_triggered)

        self.main_window.New_Bit_Layer_Action.triggered.   connect(self.menu_tab_distributor.On_new_bit_layer_action_triggered)
        self.main_window.New_Vector_Layer_Action.triggered.connect(self.menu_tab_distributor.On_new_vector_layer_action_triggered)

        self.main_window.Cancel_Selection_Action.triggered.connect(self.menu_tab_distributor.On_cancel_selection_action_triggered)
        self.main_window.Copy_Selection_Action.triggered.  connect(self.menu_tab_distributor.On_copy_selection_action_triggered)
        self.main_window.Cut_Selection_Action.triggered.   connect(self.menu_tab_distributor.On_cut_selection_action_triggered)
        self.main_window.Clear_Selection_Action.triggered. connect(self.menu_tab_distributor.On_clear_selection_action_triggered)

        self.main_window.Normal_Color_Action.triggered.    connect(self.menu_tab_distributor.On_normal_color_action_triggered)
        self.main_window.Miku_Color_Action.triggered.      connect(self.menu_tab_distributor.On_miku_color_action_triggered)
        self.main_window.Bili_Color_Action.triggered.      connect(self.menu_tab_distributor.On_bili_color_action_triggered)
        self.main_window.Red_Color_Action.triggered.       connect(self.menu_tab_distributor.On_red_color_action_triggered)
        self.main_window.Yellow_Color_Action.triggered.    connect(self.menu_tab_distributor.On_yellow_color_action_triggered)
        self.main_window.Green_Color_Action.triggered.     connect(self.menu_tab_distributor.On_green_color_action_triggered)
        self.main_window.Blue_Color_Action.triggered.      connect(self.menu_tab_distributor.On_blue_color_action_triggered)
        self.main_window.Purple_Color_Action.triggered.    connect(self.menu_tab_distributor.On_purple_color_action_triggered)
        self.main_window.White_Color_Action.triggered.     connect(self.menu_tab_distributor.On_white_color_action_triggered)
        self.main_window.Black_Color_Action.triggered.     connect(self.menu_tab_distributor.On_black_color_action_triggered)


class Main_Window(QMainWindow, Ui_Main_Window_UI):
    def __init__(self):
        super().__init__()

        self.main_window = self

        self.image_edited_flag      = False
        self.key_space_pressed_flag = False
        self.key_ctrl_pressed_flag  = False

        self.frame_view                   = Frame_View(self.main_window)
        self.frame_controller             = Frame_Controller(self.main_window)
        self.board_layer_view             = Board_Layer_View(self.main_window)
        self.board_layer_controller       = Board_Layer_Controller(self.main_window)
        self.tool_view                    = Tool_View(self.main_window)
        self.tool_controller              = Tool_Controller(self.main_window)
        self.color_controller             = Color_Controller(self.main_window)
        self.notify_controller            = Notify_Controller(self.main_window)
        self.backup_controller            = Backup_Controller(self.main_window)
        self.style_manage_controller      = Style_Manage_Controller(self.main_window)
        self.file_project_controller      = File_Project_Controller(self.main_window)
        self.menu_tab_distributor         = Menu_Tab_Distributor(self.main_window)
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
                            self.file_project_controller,
                            self.menu_tab_distributor,
                            self.event_and_singal_distributor]

        for module in self.module_list:
            module.frame_view                   = self.frame_view
            module.frame_controller             = self.frame_controller
            module.board_layer_view             = self.board_layer_view
            module.board_layer_controller       = self.board_layer_controller
            module.tool_view                    = self.tool_view
            module.tool_controller              = self.tool_controller
            module.color_controller             = self.color_controller
            module.notify_controller            = self.notify_controller
            module.backup_controller            = self.backup_controller
            module.style_manage_controller      = self.style_manage_controller
            module.file_project_controller      = self.file_project_controller
            module.menu_tab_distributor         = self.menu_tab_distributor
            module.event_and_singal_distributor = self.event_and_singal_distributor

        for module in self.module_list:
            module.init()

        self.file_project_controller.New_project((400, 200))

    def init(self):
        self.main_window.Board_Label.setFocus()

        self.main_window.Board_Label_Widget.setStyleSheet('''#Board_Label_Widget{
                                                                border:1px solid red
                                                            }''')

        self.main_window.Mix_Mod_ComboBox.setItemDelegate(QStyledItemDelegate())
        self.main_window.Mix_Mod_ComboBox.setStyleSheet('''#Mix_Mod_ComboBox QAbstractItemView::item {
                                                            margin: 2 0
                                                        }''')

        self.main_window.Pencil_Size_ComboBox.setStyleSheet('''#Pencil_Size_ComboBox QAbstractItemView{
                                                                min-width: 130px;
                                                            }''')
        self.main_window.Eraser_Size_ComboBox.setStyleSheet('''#Eraser_Size_ComboBox QAbstractItemView{
                                                                min-width: 130px;
                                                            }''')
        self.main_window.Paintbrush_Size_ComboBox.setStyleSheet('''#Paintbrush_Size_ComboBox QAbstractItemView{
                                                                min-width: 130px;
                                                            }''')


        def Set_text_in_slider(slider, min_value, max_value, current_value, left_text, right_text):
            slider.Set_min_value(min_value)
            slider.Set_max_value(max_value)
            slider.Set_current_value(current_value)
            slider.Set_left_text(left_text)
            slider.Set_right_text(right_text)

        Set_text_in_slider(self.main_window.Opacity_Slider,              0, 100, 100, '',    '100%')

        Set_text_in_slider(self.main_window.Pencil_Size_Slider,          1, 100, 10,  '×1', '10')
        Set_text_in_slider(self.main_window.Eraser_Size_Slider,          1, 100, 10,  '×1', '10')
        Set_text_in_slider(self.main_window.Paintbrush_Size_Slider,      1, 100, 10,  '×1', '10')
        Set_text_in_slider(self.main_window.Fill_Tolerance_Slider,       0, 255, 0,   '',    '0')

        Set_text_in_slider(self.main_window.Square_Outline_Width_Slider, 0, 100, 2,   '',    '2')
        self.main_window.Square_Outline_Color_Indicator_Label.Set_color(QColor(0, 0, 0))
        self.main_window.Square_Fill_Color_Indicator_Label.   Set_color(QColor(255, 255, 255))
        self.main_window.Square_X_Radius_Slider_LineEdit.     setText('0')
        self.main_window.Square_Y_Radius_Slider_LineEdit.     setText('0')
        Set_text_in_slider(self.main_window.Square_X_Radius_Slider, 0, 100, 0, '', '0')
        Set_text_in_slider(self.main_window.Square_Y_Radius_Slider, 0, 100, 0, '', '0')


        icon_base_image = Image.new('RGB', (42, 42), (0, 0, 0))

        icon_base_image.paste(Image.new('RGB', (40, 40), (240, 240, 240)), (1,1))
        self.main_window.Normal_Color_Action.setIcon(QIcon(QPixmap(icon_base_image.toqpixmap())))
        icon_base_image.paste(Image.new('RGB', (40, 40), (57,  197, 187)), (1,1))
        self.main_window.Miku_Color_Action.  setIcon(QIcon(QPixmap(icon_base_image.toqpixmap())))
        icon_base_image.paste(Image.new('RGB', (40, 40), (249, 131, 151)), (1,1))
        self.main_window.Bili_Color_Action.  setIcon(QIcon(QPixmap(icon_base_image.toqpixmap())))
        icon_base_image.paste(Image.new('RGB', (40, 40), (243, 67,  52)),  (1,1))
        self.main_window.Red_Color_Action.   setIcon(QIcon(QPixmap(icon_base_image.toqpixmap())))
        icon_base_image.paste(Image.new('RGB', (40, 40), (253, 192, 5)),   (1,1))
        self.main_window.Yellow_Color_Action.setIcon(QIcon(QPixmap(icon_base_image.toqpixmap())))
        icon_base_image.paste(Image.new('RGB', (40, 40), (138, 193, 74)),  (1,1))
        self.main_window.Green_Color_Action. setIcon(QIcon(QPixmap(icon_base_image.toqpixmap())))
        icon_base_image.paste(Image.new('RGB', (40, 40), (31,  148, 243)), (1,1))
        self.main_window.Blue_Color_Action.  setIcon(QIcon(QPixmap(icon_base_image.toqpixmap())))
        icon_base_image.paste(Image.new('RGB', (40, 40), (154, 38,  175)), (1,1))
        self.main_window.Purple_Color_Action.setIcon(QIcon(QPixmap(icon_base_image.toqpixmap())))
        icon_base_image.paste(Image.new('RGB', (40, 40), (255, 255, 255)), (1,1))
        self.main_window.White_Color_Action. setIcon(QIcon(QPixmap(icon_base_image.toqpixmap())))
        icon_base_image.paste(Image.new('RGB', (40, 40), (0,   0,   0)),   (1,1))
        self.main_window.Black_Color_Action. setIcon(QIcon(QPixmap(icon_base_image.toqpixmap())))

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

    def Get_key_ctrl_pressed_flag(self):
        return self.key_ctrl_pressed_flag

    def Set_key_ctrl_pressed_flag(self, flag):
        self.key_ctrl_pressed_flag = flag


    def Main_window_key_press_event(self, event):
        if event.key() == Qt.Key_Space:
            self.Set_key_space_pressed_flag(True)
        elif event.key() == Qt.Key_Control:
            self.Set_key_ctrl_pressed_flag(True)
        else:
            self.tool_controller.Ket_event(event)

    def Main_window_key_release_event(self, event):
        if event.key() == Qt.Key_Space:
            self.Set_key_space_pressed_flag(False)
        elif event.key() == Qt.Key_Control:
            self.Set_key_ctrl_pressed_flag(False)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Main_Window()
    sys.exit(app.exec_())
