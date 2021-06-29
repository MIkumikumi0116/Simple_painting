import io
import sys
import time
import copy
import numpy as np
from threading import Thread
from PIL import Image, ImageQt, ImageDraw, ImageOps

from PyQt5.QtWidgets import QApplication, QMainWindow, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QImage, QColor, QPainter, QPen, QPolygon
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal, QObject, QBuffer

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
            self.selected_layer_list = []

        def Insert_layer(self, layer, index = None):
            if index == None:
                self.layer_list.append(layer)
            else:
                self.layer_list.insert(index, layer)

        def Get_layer_list(self):
            return self.layer_list

        def Get_selected_layer(self):
            if len(self.selected_layer_list) == 1:
                return self.selected_layer_list[0]
            else:
                return False

        def Get_selected_layer_index(self):
            if len(self.selected_layer_list) == 1:
                return self.layer_list.index(self.selected_layer_list[0])
            else:
                return False

        def Get_selected_layer_list(self):
            return self.selected_layer_list

        def Get_selected_layer_list_index(self):
            index_list = []
            for layer in self.selected_layer_list:
                index_list.append(self.layer_list.index(layer))

            return index_list

        def Set_selected_layer(self, index_list):
            self.selected_layer_list = []
            for index in index_list:
                self.selected_layer_list.append(self.layer_list[index])

        def Append_selected_layer(self, layer):
            if layer not in self.selected_layer:
                self.selected_layer.append(layer)


    def __init__(self, main_window):
        self.main_window = main_window

        self.frame_list = []
        self.current_frame = None

    def init(self):
        self.frame_list = [None]
        self.current_frame = None


    def New_project(self):
        self.frame_list = [Frame_Controller.Frame(self)]
        self.current_frame = self.frame_list[0]

        self.current_frame.Insert_layer(self.board_layer_controller.Yield_bit_layer())
        self.board_layer_controller.Draw_painting_new_project()


    def Get_frame_list(self):
        return self.frame_list

    def Set_frame_list(self, frame_list):
        self.frame_list = frame_list

    def Get_current_frame(self):
        return self.current_frame

    def Set_current_frame(self, index):
        self.current_frame = self.frame_list[index]


class Board_Layer_View:
    def __init__(self, main_window):
        self.main_window = main_window

        self.board_image = None

        self.camera_zoom       = None
        self.camera_rotate     = 0
        self.camera_offset     = (0, 0)
        self.camera_board_size = (None ,None)

        self.first_click_board_pos  = None  #用于选择摄像机
        self.second_click_board_pos = None

        self.CAMERMA_ZOOM_MAX = 50
        self.CAMERMA_ZOOM_MIN = -20

    def init(self):
        self.board_image      = None
        self.camera_zoom       = None
        self.camera_board_size = None

        self.first_click_board_pos  = None
        self.second_click_board_pos = None


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
            camera_offset_array   = np.array([float(-camera_offset[0]), float(-camera_offset[1])])
            camera_offset_array   = inverse_scale_matrix @ inverse_rotate_matrix @ camera_offset_array

            viewport_pos_list = [np.array([-label_size[0] / 1.8, -label_size[1] / 1.8]),
                                 np.array([ label_size[0] / 1.8, -label_size[1] / 1.8]),
                                 np.array([-label_size[0] / 1.8,  label_size[1] / 1.8]),
                                 np.array([ label_size[0] / 1.8,  label_size[1] / 1.8])]
            viewport_pos_inverse_transform = lambda viewport_pos : inverse_scale_matrix @ inverse_rotate_matrix @ viewport_pos - camera_offset_array
            viewport_pos_list = list(map(viewport_pos_inverse_transform, viewport_pos_list))

            board_extend = (label_size[0] ** 2 + label_size[1] ** 2) ** 0.5 / camera_zoom * 1.2
            r, g, b, _   = self.style_manage_controller.Get_highlight_back_color().getRgb()
            image        = ImageOps.expand(image, border = round(board_extend), fill=(r, g, b))

            image_array  = np.array(image)
            image_mask   = Image.new('1', (image.size[1], image.size[0]), 0)
            mask_polygon = [(round(viewport_pos_list[0][0] + image.size[0] / 2), round(viewport_pos_list[0][1] + image.size[0] / 2)),
                            (round(viewport_pos_list[1][0] + image.size[0] / 2), round(viewport_pos_list[1][1] + image.size[0] / 2)),
                            (round(viewport_pos_list[3][0] + image.size[0] / 2), round(viewport_pos_list[3][1] + image.size[0] / 2)),
                            (round(viewport_pos_list[2][0] + image.size[0] / 2), round(viewport_pos_list[2][1] + image.size[0] / 2))]
            ImageDraw.Draw(image_mask).polygon(mask_polygon, outline = 1, fill = 1)
            mask_array   = np.array(image_mask)

            image_array[:, :, 0] *= mask_array
            image_array[:, :, 1] *= mask_array
            image_array[:, :, 2] *= mask_array
            image_array[:, :, 3] *= mask_array
            image = Image.fromarray(image_array, "RGBA")
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
            label_background_image = Image.new('RGBA',
                                              (label_size[0], label_size[1]),
                                              (r, g, b))
            label_background_image.paste(image, (0, 0), mask = image)
            image = label_background_image

        image = self.Print_promet_layer(image)
        self.main_window.Board_Label.setPixmap(ImageQt.toqpixmap(image))

    def Print_image_new_project(self, image):
        # init board_image, camera_zoom, camera_board_size
        self.board_image = image.copy()

        self.camera_zoom       = None
        self.camera_rotate     = 0
        self.camera_offset     = (0, 0)
        self.camera_board_size = (None ,None)

        self.first_click_pos   = None
        self.second_click_pos  = None

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
            image_transferred = image.resize((image_size[0] * camera_zoom, image_size[1] * camera_zoom), Image.NEAREST)

        elif narrow_type == 'h_narrow':
            camera_zoom = -(image_size[0] // label_size[0] + 1)
            image_transferred = image.resize((image_size[0] // -camera_zoom, image_size[1] // -camera_zoom), Image.NEAREST)

        elif narrow_type == 'v_narrow':
            camera_zoom = -(image_size[1] // label_size[1] + 1)
            image_transferred = image.resize((image_size[0] // -camera_zoom, image_size[1] // -camera_zoom), Image.NEAREST)

        r, g, b, _ = self.style_manage_controller.Get_highlight_back_color().getRgb()
        label_background_image = Image.new('RGBA',
                                           (label_size[0], label_size[1]),
                                           (r, g, b))
        label_background_image.paste(image_transferred, ((label_size[0] - image_transferred.size[0]) // 2,
                                                         (label_size[1] - image_transferred.size[1]) // 2))

        self.camera_zoom = camera_zoom
        self.camera_board_size = image_transferred.size
        self.Set_h_scrollbar()
        self.Set_v_scrollbar()
        self.main_window.Board_Label.setPixmap(ImageQt.toqpixmap(label_background_image))
        self.Update_layer_widget_list()

    def Print_promet_layer(self, image):
        command = self.board_layer_controller.Get_promet_layer_command()
        if command == None:
            return image

        camera_zoom   =  self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
        camera_rotate =  self.camera_rotate
        camera_offset =  self.camera_offset
        board_size    =  self.board_layer_controller.Get_board_size()
        label_size    = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())

        if command.order_enum == 'draw_rect_solid_line':
            board_first_point  = command.data[0]
            board_second_point = command.data[1]

            vertex_pos_list    = [(board_first_point[0] , board_first_point[1]),
                                  (board_second_point[0], board_first_point[1]),
                                  (board_second_point[0], board_second_point[1]),
                                  (board_first_point[0] , board_second_point[1])]
            vertex_pos_list    = map(lambda vertex_pos : self.Board_pos_to_label_pos(vertex_pos[0], vertex_pos[1]), vertex_pos_list)
            vertex_pos_list    = list(map(lambda vertex_pos : QPoint(vertex_pos[0], vertex_pos[1]), vertex_pos_list))

            promet_image = QImage(label_size[0], label_size[1], QImage.Format_ARGB32)
            painter      = QPainter(promet_image)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QPen(QColor(0, 0, 0, 255)))
            painter.drawPolygon(QPolygon(vertex_pos_list))
            painter.end()

            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            promet_image.save(buffer, "PNG")
            promet_image = Image.open(io.BytesIO(buffer.data()))
            image.paste(promet_image, mask = promet_image)
            return image

        elif command.order_enum == 'draw_rect_dotted_line':
            board_first_point  = command.data[0]
            board_second_point = command.data[1]

            vertex_pos_list    = [(board_first_point[0] , board_first_point[1]),
                                  (board_second_point[0], board_first_point[1]),
                                  (board_second_point[0], board_second_point[1]),
                                  (board_first_point[0] , board_second_point[1])]
            vertex_pos_list    = map(lambda vertex_pos : self.Board_pos_to_label_pos(vertex_pos[0], vertex_pos[1]), vertex_pos_list)
            vertex_pos_list    = list(map(lambda vertex_pos : QPoint(vertex_pos[0], vertex_pos[1]), vertex_pos_list))

            promet_image = QImage(label_size[0], label_size[1], QImage.Format_ARGB32)
            painter      = QPainter(promet_image)
            painter.setRenderHint(QPainter.Antialiasing)
            pen = QPen(QColor(0, 0, 0, 255))
            pen.setStyle(Qt.DashLine)
            painter.setPen(pen)
            painter.drawPolygon(QPolygon(vertex_pos_list))
            painter.end()

            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            promet_image.save(buffer, "PNG")
            promet_image = Image.open(io.BytesIO(buffer.data()))
            image.paste(promet_image, mask = promet_image)
            return image


    def Update_offset(self, offset):
        self.camera_offset = offset
        self.Print_image(self.board_image)

    def Zoom_in(self, label_x, label_y):
        if self.camera_zoom + 1 <= self.CAMERMA_ZOOM_MAX:
            original_camera_zoom       = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
            self.camera_zoom           = self.camera_zoom + 1 if self.camera_zoom + 1 not in (0, -1) else 1
            transferred_camera_zoom    = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom

            label_size      = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())
            original_offset =  self.camera_offset

            original_board_offset_x    = original_offset[0] - label_size[0] / 2 + label_x
            original_board_offset_y    = original_offset[1] - label_size[1] / 2 + label_y

            transferred_board_offset_x = original_board_offset_x / original_camera_zoom * transferred_camera_zoom
            transferred_board_offset_y = original_board_offset_y / original_camera_zoom * transferred_camera_zoom

            transferred_offset_x       = transferred_board_offset_x + label_size[0] / 2 - label_x
            transferred_offset_y       = transferred_board_offset_y + label_size[1] / 2 - label_y

            self.Update_camera_board_size()

            transferred_offset_x       = max(-self.camera_board_size[0], min(transferred_offset_x, self.camera_board_size[0]))
            transferred_offset_y       = max(-self.camera_board_size[1], min(transferred_offset_y, self.camera_board_size[1]))
            self.camera_offset         = (round(transferred_offset_x), round(transferred_offset_y))

            self.Set_h_scrollbar()
            self.Set_v_scrollbar()
            self.Print_image(self.board_image)

    def Zoom_out(self, label_x, label_y):
        if self.camera_zoom - 1 >= self.CAMERMA_ZOOM_MIN:
            original_camera_zoom       = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
            self.camera_zoom           = self.camera_zoom - 1 if self.camera_zoom - 1 not in (1, 0) else -1
            transferred_camera_zoom    = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom

            label_size      = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())
            original_offset =  self.camera_offset

            original_board_offset_x    = original_offset[0] - label_size[0] / 2 + label_x
            original_board_offset_y    = original_offset[1] - label_size[1] / 2 + label_y

            transferred_board_offset_x = original_board_offset_x / original_camera_zoom * transferred_camera_zoom
            transferred_board_offset_y = original_board_offset_y / original_camera_zoom * transferred_camera_zoom

            transferred_offset_x       = transferred_board_offset_x + label_size[0] / 2 - label_x
            transferred_offset_y       = transferred_board_offset_y + label_size[1] / 2 - label_y

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
        camera_offset_array = scale_matrix @ rotate_matrix @ board_offset


        self.camera_rotate = camera_rotate
        self.camera_offset = (round(camera_offset_array[0]), round(camera_offset_array[1]))

        self.Update_camera_board_size()
        self.Set_h_scrollbar()
        self.Set_v_scrollbar()
        self.Print_image(self.board_image)


    def Label_pos_to_board_pos(self, label_x, label_y):
        camera_zoom       = self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
        camera_rotate     = self.camera_rotate
        camera_offset     = self.camera_offset
        camera_board_size = self.camera_board_size

        board_size     =  self.board_layer_controller.Get_board_size()
        label_size     = (self.main_window.Board_Label.width(), self.main_window.Board_Label.height())

        camera_board_x = camera_offset[0] - label_size[0] / 2 + label_x
        camera_board_y = camera_offset[1] - label_size[1] / 2 + label_y

        angle          = np.radians(camera_rotate)
        cos, sin       = np.cos(angle), np.sin(angle)
        inverse_rotate_matrix = np.array([[ cos, sin],
                                          [-sin, cos]])
        inverse_scale_matrix  = np.array([[1 / camera_zoom , 0],
                                          [0, 1 / camera_zoom]])
        board_array = np.array([float(camera_board_x), float(camera_board_y)])
        board_array = inverse_rotate_matrix @ inverse_scale_matrix @ board_array + np.array([board_size[0] / 2, board_size[1] / 2])

        return round(board_array[0]), round(board_array[1])

    def Board_pos_to_label_pos(self, board_x, board_y):
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
        to_label_pos_correct_array = np.array([float(label_size[0] / 2), float(label_size[1] / 2)])

        board_array = np.array([board_x - board_size[0] / 2, board_y - board_size[1] / 2])
        label_array = scale_matrix @ rotate_matrix @ board_array - offset_array + to_label_pos_correct_array

        return round(label_array[0]), round(label_array[1])

    def Update_camera_board_size(self):
        camera_zoom   =  self.camera_zoom if self.camera_zoom > 0 else -1 / self.camera_zoom
        camera_rotate =  self.camera_rotate
        image_size    =  self.board_image.size

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

    def Rotate_board_by_mouse(self, label_x, label_y, first_press_flag):
        if first_press_flag:
            self.first_click_board_pos = (label_x, label_y)
            return
        else:
            self.second_click_board_pos = (label_x, label_y)

        if (self.first_click_board_pos[0] - self.second_click_board_pos[0]) ** 2 + \
           (self.first_click_board_pos[1] - self.second_click_board_pos[1]) ** 2 > 100:
            first_pos  = self.first_click_board_pos
            second_pos = self.second_click_board_pos
            center_pos = (self.main_window.Board_Label.width() / 2, self.main_window.Board_Label.height() / 2)

            first_pos_vector  = np.array([first_pos[0]  - center_pos[0], first_pos[1]  - center_pos[1]])
            second_pos_vector = np.array([second_pos[0] - center_pos[0], second_pos[1] - center_pos[1]])

            first_len   = np.sqrt(first_pos_vector  @ first_pos_vector )
            second_len  = np.sqrt(second_pos_vector @ second_pos_vector)

            angle_cos   = first_pos_vector @ second_pos_vector / (first_len * second_len)
            delta_angle = np.arccos(angle_cos)
            delta_angle = delta_angle * 360 / 2 / np.pi

            if np.cross(first_pos_vector, second_pos_vector) > 0:
                self.Rotate_board(delta_angle)
            else:
                self.Rotate_board(-delta_angle)

            self.first_click_board_pos = self.second_click_board_pos

    def Update_layer_widget_list(self):
        for layer_widget in self.main_window.Layer_List_ScrollArea.findChildren(Layer_Widget):
            self.main_window.Layer_List_ScrollArea_Layout.removeWidget(layer_widget)
            layer_widget.deleteLater()

        spacer = self.main_window.Layer_List_ScrollArea_Layout.itemAt(0)
        if spacer:
            self.main_window.Layer_List_ScrollArea_Layout.removeItem(spacer)
            del spacer

        for layer in self.board_layer_controller.Get_layer_list():
            layer.Set_widget(self.Yield_layer_widget())
            layer.Set_selected_state_enum('unselected')
            self.main_window.Layer_List_ScrollArea_Layout.addWidget(layer.widget)

        for layer in self.board_layer_controller.Get_selected_layer_list():
            layer.Set_selected_state_enum('weak_selected')

        if len(self.board_layer_controller.Get_selected_layer_list()) >= 0:
            self.main_window.Layer_Name_LineEdit.setEnabled(True)
            self.main_window.Mix_Mod_ComboBox.setEnabled(True)
            self.main_window.Opacity_Slider.setEnabled(True)

            strong_selected_layer = self.board_layer_controller.Get_selected_layer_list()[0]
            strong_selected_layer.Set_selected_state_enum('strong_selected')

            self.main_window.Layer_Name_LineEdit.setText(strong_selected_layer.Get_name())
            mod_index = self.main_window.Mix_Mod_ComboBox.findText(strong_selected_layer.Get_mod_enum(), Qt.MatchFixedString)
            self.main_window.Mix_Mod_ComboBox.setCurrentIndex(mod_index)
            self.main_window.Opacity_Slider.Set_current_value(strong_selected_layer.Get_opacity())
            self.main_window.Opacity_Slider.Set_right_text(str(strong_selected_layer.Get_opacity()))
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

    def On_new_bit_layer_action_triggered(self):
        self.board_layer_controller.Add_bit_layer()

    def On_cancel_selection_action_triggered(self):
        self.board_layer_controller.Cancel_selection()

    def On_copy_selection_action_triggered(self):
        self.board_layer_controller.Copy_selection()

    def On_cut_selection_action_triggered(self):
        self.board_layer_controller.Cut_Selection()

    def On_layer_name_lineedit_text_changed(self, text):
        selected_layer = self.board_layer_controller.Get_selected_layer()
        if selected_layer == None:
            self.Notify_Controller.Send_label_notify('该设置只能作用于单个图层')
            return

        selected_layer.Set_name(text)

    def On_mix_mod_combobox_text_changed(self, text):
        selected_layer = self.board_layer_controller.Get_selected_layer()
        if selected_layer == None:
            self.Notify_Controller.Send_label_notify('该设置只能作用于单个图层')
            return

        selected_layer.Set_mod_enum(text)
        self.board_layer_controller.Draw_painting()

    def On_opacity_slider_value_change(self, value):
        selected_layer = self.board_layer_controller.Get_selected_layer()
        if selected_layer == None:
            self.Notify_Controller.Send_label_notify('该设置只能作用于单个图层')
            return

        selected_layer.Set_opacity(value)
        self.main_window.Opacity_Slider.Set_current_value(selected_layer.Get_opacity())
        self.main_window.Opacity_Slider.Set_right_text(str(selected_layer.Get_opacity()))
        self.board_layer_controller.Draw_painting()


    def Wheel_Event(self, event):
        label_x, label_y  = event.position().x(), event.position().y()

        if event.angleDelta().y() > 0:
            self.Zoom_in(label_x, label_y)
        else:
            self.Zoom_out(label_x, label_y)

    def Mouse_press_event(self, event):
        label_x, label_y = event.pos().x(), event.pos().y()
        board_x, board_y = self.Label_pos_to_board_pos(label_x, label_y)
        board_size = self.board_layer_controller.Get_board_size()

        if event.button() == Qt.MiddleButton:
            self.Rotate_board_by_mouse(label_x, label_y, first_press_flag = True)
        elif 0 <= board_x < board_size[0] and 0 <= board_y < board_size[1]:
            self.tool_controller.Mouse_press_event(label_x, label_y, board_x, board_y, event)

    def Mouse_move_event(self, event):
        label_x, label_y = event.pos().x(), event.pos().y()
        board_x, board_y = self.Label_pos_to_board_pos(label_x, label_y)
        board_size = self.board_layer_controller.Get_board_size()

        if event.buttons() == Qt.MiddleButton:
            self.Rotate_board_by_mouse(label_x, label_y, first_press_flag = False)
        elif 0 <= board_x < board_size[0] and 0 <= board_y < board_size[1]:
            self.tool_controller.Mouse_move_event(label_x, label_y, board_x, board_y, event)

    def Mouse_release_event(self, event):
        label_x, label_y = event.pos().x(), event.pos().y()
        board_x, board_y = self.Label_pos_to_board_pos(label_x, label_y)
        board_size = self.board_layer_controller.Get_board_size()

        if event.button() == Qt.MiddleButton:
            self.Rotate_board_by_mouse(label_x, label_y, first_press_flag = False)
        elif 0 <= board_x < board_size[0] and 0 <= board_y < board_size[1]:
            self.tool_controller.Mouse_release_event(label_x, label_y, board_x, board_y, event)


class Board_Layer_Controller:

    class Promet_Layer_Command_Struct:
        def __init__(self):
            self.order_enum  = None
            self.caller_enum = None
            self.data        = None

    class Selection_Mask:
        def __init__(self, controller, type_enum, selection_vector):
            self.controller = controller

            self.type_enum  = type_enum
            self.mask_image = self.Draw_mask(selection_vector)

        def Draw_mask(self, selection_vector):
            mask_image = Image.new('1', self.controller.Get_board_size(), 0)

            if self.type_enum == 'rect':
                ImageDraw.Draw(mask_image).rectangle(selection_vector.data, outline = 1, fill = 1)
                return mask_image

    class Bit_Layer:
        next_layer_index = 1

        def __init__(self, controller, widget, image = None, offset = (0, 0), name = '', mod_enum = '正常', opacity = 100):
            self.layer_type_enum     = 'bit_layer'
            self.selected_state_enum = 'unselected'

            self.controller          = controller
            self.widget              = widget
            self.widget.init(self, self.controller.style_manage_controller)
            self.widget.Hide_Button.clicked.connect(self.On_hide_button_clicked)
            self.widget.Lock_Button.clicked.connect(self.On_lock_button_clicked)
            self.widget.mouse_press_singal.connect(self.On_mouse_press_singal_emit)

            self.image = image if image != None else Image.new('RGBA',
                                                               self.controller.Get_board_size(),
                                                              (255, 255, 255, 0))
            self.offset = offset

            self.hide_flag = False
            self.lock_flag = False
            if name != '':
                self.name = name
            else:
                self.name = f'图层{controller.Bit_Layer.next_layer_index}'
                controller.Bit_Layer.next_layer_index += 1
            self.mod_enum = mod_enum
            self.opacity = opacity

            self.Set_preview_label()
            self.Set_widget_info()

        def Draw_layer(self):
            return self.image.copy()

        def Set_preview_label(self):
            r, g, b, _ = self.controller._Get_highlight_back_color().getRgb()
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

        def Set_widget_info(self):
            self.widget.Set_widget_info()


        def On_hide_button_clicked(self):
            self.hide_flag = not self.hide_flag
            self.Set_widget_info()
            self.controller.Draw_painting()

        def On_lock_button_clicked(self):
            self.lock_flag = not self.lock_flag
            self.Set_widget_info()

        def On_mouse_press_singal_emit(self):
            self.controller.Change_select_state(self)


        def Get_selected_state_enum(self):
            return self.selected_state_enum

        def Set_selected_state_enum(self, selected_state_enum):
            self.selected_state_enum = selected_state_enum
            self.Set_widget_info()

        def Set_widget(self, widget):
            self.widget = widget
            self.widget.init(self, self.controller.style_manage_controller)
            self.widget.Hide_Button.clicked.connect(self.On_hide_button_clicked)
            self.widget.Lock_Button.clicked.connect(self.On_lock_button_clicked)
            self.widget.mouse_press_singal.connect(self.On_mouse_press_singal_emit)
            self.Set_preview_label()
            self.Set_widget_info()

        def Get_image(self):
            return self.image

        def Set_image(self, image):
            self.image = image.copy()
            self.Set_preview_label()

        def Get_layer_size(self):
            return self.image.size

        def Get_offset(self):
            return self.offset

        def Set_offset(self, offset):
            self.offset = offset

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


    def __init__(self, main_window):
        self.main_window = main_window

        self.board_size           = (256, 256)
        self.current_frame        = None
        self.selection_mask       = None
        self.promet_layer_command = None

        self.painting             = Image.new('RGBA', self.board_size, (255, 255, 255))
        self.background_layer     = Image.new('RGBA', self.board_size, (255, 255, 255))

    def init(self):
        self.current_frame        = None
        self.selection_mask       = None
        self.promet_layer_command = None


    def Genrate_painting(self):
        painting = self.background_layer.copy()
        for layer in self.Get_layer_list()[::-1]:
            if not layer.Get_hide_flag():
                layer_image = layer.Draw_layer()
                layer_image_array = np.array(layer_image, dtype = 'float64')
                layer_image_array[:, :, 3] *= layer.Get_opacity() / 100
                layer_image = Image.fromarray(layer_image_array.astype(np.uint8))

                if layer.offset[0] < 0:
                    layer_image = layer_image.crop((-layer.offset[0], 0, layer_image.size[0], layer_image.size[1]))
                if layer.offset[1] < 0:
                    layer_image = layer_image.crop((0, -layer.offset[1], layer_image.size[0], layer_image.size[1]))
                if layer.offset[0] + layer_image.size[0] > self.board_size[0]:
                    layer_image = layer_image.crop((0, 0, layer.offset[0] + layer_image.size[0] - self.board_size[0], layer_image.size[1]))
                if layer.offset[1] + layer_image.size[1] > self.board_size[1]:
                    layer_image = layer_image.crop((0, 0, layer_image.size[0], layer.offset[1] + layer_image.size[1] - self.board_size[1]))

                if layer.mod_enum == '正常':
                    painting.paste(layer_image, (layer.offset[0],layer.offset[1]), mask = layer_image)

        return painting

    def Draw_painting(self):
        painting = self.Genrate_painting()

        self.painting = painting.copy()
        self.board_layer_view.Print_image(painting)

    def Draw_painting_new_project(self):
        self.current_frame = self.frame_controller.Get_current_frame()
        self.current_frame.Set_selected_layer([0])
        self.Get_selected_layer().Set_selected_state_enum('strong_selected')
        self.selection_mask       = None
        self.promet_layer_command = None

        painting = self.Genrate_painting()

        self.painting = painting.copy()
        self.board_layer_view.Print_image_new_project(painting)
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
            self.promet_layer_command.order_enum  = 'draw_rect_solid_line'
            self.promet_layer_command.caller_enum = 'prompt_selection'
            self.promet_layer_command.data        = selection_vector.data

            self.board_layer_view.Print_image(self.painting)

    def Crate_selection(self, selection_vector):
        if selection_vector.type_enum == 'rect_selection':
            self.promet_layer_command = Board_Layer_Controller.Promet_Layer_Command_Struct()
            self.promet_layer_command.order_enum  = 'draw_rect_dotted_line'
            self.promet_layer_command.caller_enum = 'crate_selection'
            self.promet_layer_command.data        = selection_vector.data

            self.board_layer_view.Print_image(self.painting)

            self.selection_mask = Board_Layer_Controller.Selection_Mask(self, 'rect', selection_vector)

    def Cancel_selection(self):
        if (not self.promet_layer_command is None) and self.promet_layer_command.caller_enum == 'crate_selection':
            self.Clear_promet_layer_command()

        self.selection_mask = None

        self.board_layer_view.Print_image(self.painting)

    def Copy_selection(self):
        if self.selection_mask == None:
            self.notify_controller.Send_label_notify('尚未建立选区')
            return
        selected_layer = self.Get_selected_layer()
        if selected_layer == False:
            self.notify_controller.Send_label_notify('该工具只能作用于单个图层')
            return
        if selected_layer.Get_lock_flag():
            self.notify_controller.Send_label_notify('该图层已锁定')
            return

        image = Image.new('RGBA', self.board_size, (0, 0, 0, 0))
        image.paste(selected_layer.Get_image(), mask = self.selection_mask.mask_image)

        bonding_box = image.getbbox()
        if bonding_box == None:
            self.notify_controller.Send_label_notify('选定的区域内没有像素')
            return
        image = image.crop(bonding_box)
        offset = (bonding_box[0], bonding_box[1])

        new_layer = Board_Layer_Controller.Bit_Layer(controller = self, widget = self.board_layer_view.Yield_layer_widget(), image = image, offset = offset)
        self.Insert_layer(new_layer, self.Get_selected_layer_index())

        self.board_layer_view.Update_layer_widget_list()
        self.Cancel_selection()
        self.backup_controller.Add_backup()

    def Cut_Selection(self):
        if self.selection_mask == None:
            self.notify_controller.Send_label_notify('尚未建立选区')
            return
        selected_layer = self.Get_selected_layer()
        if selected_layer == False:
            self.notify_controller.Send_label_notify('该工具只能作用于单个图层')
            return
        if selected_layer.Get_lock_flag():
            self.notify_controller.Send_label_notify('该图层已锁定')
            return

        image = Image.new('RGBA', self.board_size, (0, 0, 0, 0))
        image.paste(selected_layer.Get_image(), mask = self.selection_mask.mask_image)

        bonding_box = image.getbbox()
        if bonding_box == None:
            self.notify_controller.Send_label_notify('选定的区域内没有像素')
            return
        image = image.crop(bonding_box)
        offset = (bonding_box[0], bonding_box[1])

        new_layer = Board_Layer_Controller.Bit_Layer(controller = self, widget = self.board_layer_view.Yield_layer_widget(), image = image, offset = offset)
        self.Insert_layer(new_layer, self.Get_selected_layer_index())

        blank_image = Image.new('RGBA', self.board_size, (255, 255, 255, 0))
        layer_image = selected_layer.Get_image()
        layer_image.paste(blank_image, mask = self.selection_mask.mask_image)
        selected_layer.Set_image(layer_image)

        self.board_layer_view.Update_layer_widget_list()
        self.Cancel_selection()
        self.backup_controller.Add_backup()


    def Yield_bit_layer(self):
        return Board_Layer_Controller.Bit_Layer(self, self.board_layer_view.Yield_layer_widget())

    def Add_bit_layer(self):
        new_layer = Board_Layer_Controller.Bit_Layer(self, self.board_layer_view.Yield_layer_widget())
        self.Insert_layer(new_layer, 0)
        self.board_layer_view.Update_layer_widget_list()
        self.backup_controller.Add_backup()

    def Change_select_state(self, layer):
        selected_layer_index_list = self.Get_selected_layer_list_index()
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


    def Get_board_size(self):
        return self.board_size

    def Insert_layer(self, layer, index = None):
        self.current_frame.Insert_layer(layer) if index == None else self.current_frame.Insert_layer(layer, index)

    def Get_layer_list(self):
        return self.current_frame.Get_layer_list()

    def Get_selected_layer(self):
        return self.current_frame.Get_selected_layer()

    def Get_selected_layer_index(self):
        return self.current_frame.Get_selected_layer_index()

    def Get_selected_layer_list(self):
        return self.current_frame.Get_selected_layer_list()

    def Get_selected_layer_list_index(self):
        return self.current_frame.Get_selected_layer_list_index()

    def Set_selected_layer(self, index_list):
         self.current_frame.Set_selected_layer(index_list)

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

    def init(self):
        pass

    def On_pencil_button_clicked(self):
        self.tool_controller.Select_pencil()

    def On_rect_selection_button_clicked(self):
        self.tool_controller.Select_rect_selection()


class Tool_Controller:
    class Selection_Vector_Struct:
        def __init__(self):
            self.type_enum  = None
            self.data       = None

    class Pencil_Tool:
        def __init__(self, controller):
            self.controller = controller

            self.brush_size = 20

        def Constructor(self):
            pass

        def Destructor(self):
            pass


        def Pencil_draw(self, board_x, board_y):
            layer = self.controller._Get_selected_layer()
            if layer == False:
                self.controller._Send_label_notify('该工具只能作用于单个图层')
                return
            if layer.Get_lock_flag():
                self.controller._Send_label_notify('该图层已锁定')
                return

            self.controller._Set_image_edited()

            board_size = self.controller._Get_board_size()
            layer_image = Image.new('RGBA', board_size, (0, 0, 0, 0))
            layer_image.paste(layer.Get_image(), layer.Get_offset())

            if 0 <= board_x < layer_image.size[0] and 0 <= board_y < layer_image.size[1]:
                radius = self.brush_size // 2
                pixel_matrix_np = np.array(layer_image, dtype = 'uint8')

                color = self.controller._Get_front_color()
                r, g, b, _ = color.getRgb()
                defult_color = np.array((r, g, b, 255))

                # TODO 插值
                painting_order = [(i, j,
                                   defult_color
                                  if ((i - board_x) ** 2 + (j - board_y) ** 2 <= (radius) ** 2)
                                  else (((radius + 1) ** 2 - (radius) ** 2) - ((i - board_x) ** 2 + (j - board_y) ** 2 - (radius) ** 2)) / ((radius + 1) ** 2 - (radius) ** 2))

                                  for i in range(board_x - radius, board_x + radius + 1)
                                  for j in range(board_y - radius, board_y + radius + 1)
                                  if (i - board_x) ** 2 + (j - board_y) ** 2 <= (radius + 1) ** 2
                                  and 0 <= i < board_size[0] and 0 <= j < board_size[1]]

                for point in painting_order:
                    if str(type(point[2])) == "<class 'numpy.ndarray'>":
                        pixel_matrix_np[point[1], point[0]] = defult_color
                    # else:
                    #     pixel_matrix_np[point[1], point[0]] = np.array([r + (255 - r) * point[2],
                    #                                                     g + (255 - g) * point[2],
                    #                                                     b + (255 - b) * point[2],
                    #                                                     255])

                layer_image = Image.fromarray(pixel_matrix_np)

                if layer.Get_layer_size() == board_size and layer.Get_offset() == (0, 0):
                    layer.Set_image(layer_image)
                    layer.Set_offset((0, 0))
                else:
                    bonding_box = layer_image.getbbox()
                    layer.Set_image(layer_image)
                    layer.Set_offset((bonding_box[0], bonding_box[1]))

                layer.Set_preview_label()
                self.controller._Draw_painting()


        def Mouse_press_event(self, board_x, board_y, event):
            if event.button() == Qt.LeftButton:
                self.Pencil_draw(board_x, board_y)

        def Mouse_move_event(self, board_x, board_y, event):
            if event.buttons() == Qt.LeftButton:
                self.Pencil_draw(board_x, board_y)

        def Mouse_release_event(self, board_x, board_y, event):
            if event.button() == Qt.LeftButton:
                self.Pencil_draw(board_x, board_y)
                self.controller._Add_backup()

    class Rect_Selection:
        def __init__(self, controller):
            self.controller = controller

            self.first_point      = None
            self.second_point     = None

            self.selection_vector = None

        def Constructor(self):
            pass

        def Destructor(self):
            pass


        def Prompt_selection_vector(self, board_x, board_y):
            if self.first_point == None:
                self.first_point = (board_x, board_y)
                return

            self.second_point = (board_x, board_y)

            self.selection_vector = Tool_Controller.Selection_Vector_Struct()
            self.selection_vector.type_enum  = 'rect_selection'
            self.selection_vector.data = [None, None]
            self.selection_vector.data[0] = min([self.first_point, self.second_point], key = lambda point : point[0])
            self.selection_vector.data[1] = max([self.first_point, self.second_point], key = lambda point : point[0])

            self.controller._Prompt_selection_vector(self.selection_vector)

        def Crate_selection_vector(self, board_x, board_y):
            self.second_point = (board_x, board_y)

            self.selection_vector = Tool_Controller.Selection_Vector_Struct()
            self.selection_vector.type_enum  = 'rect_selection'
            self.selection_vector.data = [None, None]
            self.selection_vector.data[0] = min([self.first_point, self.second_point], key = lambda point : point[0])
            self.selection_vector.data[1] = max([self.first_point, self.second_point], key = lambda point : point[0])

            self.controller._Crate_selection_vector(self.selection_vector)


        def Mouse_press_event(self, board_x, board_y, event):
            if event.button() == Qt.LeftButton:
                self.first_point      = None
                self.second_point     = None
                self.selection_vector = None

                self.Prompt_selection_vector(board_x, board_y)

        def Mouse_move_event(self, board_x, board_y, event):
            if event.buttons() == Qt.LeftButton:
                self.Prompt_selection_vector(board_x, board_y)

        def Mouse_release_event(self, board_x, board_y, event):
            if event.button() == Qt.LeftButton:
                self.Crate_selection_vector(board_x, board_y)


    def __init__(self, main_window):
        self.main_window = main_window

        self.current_tool = None

        self.pencil_tool = Tool_Controller.Pencil_Tool(self)
        self.rect_selection = Tool_Controller.Rect_Selection(self)

        self.board_pos_only_list = [self.pencil_tool, self.rect_selection]
        self.label_pos_only_list = [self.rect_selection]

    def init(self):
        self.current_tool = self.pencil_tool
        self.current_tool.Constructor()


    def Mouse_press_event(self, label_x, label_y, board_x, board_y, event):
        if self.current_tool in self.board_pos_only_list:
            self.current_tool.Mouse_press_event(board_x, board_y, event)
        elif self.current_tool in self.label_pos_only_list:
            self.current_tool.Mouse_press_event(label_x, label_y, event)

    def Mouse_move_event(self, label_x, label_y, board_x, board_y, event):
        if self.current_tool in self.board_pos_only_list:
            self.current_tool.Mouse_move_event(board_x, board_y, event)
        elif self.current_tool in self.label_pos_only_list:
            self.current_tool.Mouse_move_event(label_x, label_y, event)

    def Mouse_release_event(self, label_x, label_y, board_x, board_y, event):
        if self.current_tool in self.board_pos_only_list:
            self.current_tool.Mouse_release_event(board_x, board_y, event)
        elif self.current_tool in self.label_pos_only_list:
            self.current_tool.Mouse_release_event(label_x, label_y, event)

    def Select_pencil(self):
        self.current_tool.Destructor()
        self.current_tool = self.pencil_tool
        self.current_tool.Constructor()

    def Select_rect_selection(self):
        self.current_tool.Destructor()
        self.current_tool = self.rect_selection
        self.current_tool.Constructor()


    def _Get_selected_layer(self):
        return self.board_layer_controller.Get_selected_layer()

    def _Send_label_notify(self, text):
        self.notify_controller.Send_label_notify(text)

    def _Set_image_edited(self):
        self.main_window.Set_image_edited_flag(True)

    def _Get_board_size(self):
        return self.board_layer_controller.Get_board_size()

    def _Get_front_color(self):
        return self.color_controller.Get_front_color()

    def _Draw_painting(self):
        self.board_layer_controller.Draw_painting()

    def _Prompt_selection_vector(self, selection_vector):
        self.board_layer_controller.Prompt_selection(selection_vector)

    def _Crate_selection_vector(self, selection_vector):
        self.board_layer_controller.Crate_selection(selection_vector)

    def _Add_backup(self):
        self.backup_controller.Add_backup()


class Color_Controller:
    def __init__(self, main_window):
        self.main_window = main_window

        self.front_color = QColor(0, 0, 0)
        self.back_color  = QColor(255, 255, 255)

    def init(self):
        self.main_window.Color_Picker_Widget.color_change_singal.connect(self.On_color_change_singal_emit)
        self.main_window.Color_Indicator_Widget.switch_color_singal.connect(self.On_switch_color_singal_emit)

        self.main_window.Color_Indicator_Widget.Set_front_color(self.front_color)
        self.main_window.Color_Indicator_Widget.Set_back_color(self.back_color)
        self.main_window.Color_Picker_Widget.Set_current_color(self.front_color)


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
    release_label_notify_singal = pyqtSignal(str)

    def __init__(self, main_window):
        self.main_window = main_window
        super().__init__()

        self.label_notify_list = []
        self.label_notify_thread = Thread(target = self._Label_notify_thread_action, args = ())
        self.label_notify_thread.start()
        self.release_label_notify_singal.connect(self._Release_label_notify)
        self.label_notify_busy_flag = False
        self.label_notify_timer = QTimer()
        self.label_notify_timer.timeout.connect(self._On_label_notify_timer_timeout)

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
            self.frame_list                = []
            self.current_frame_index       = None

    class Frame_Backup_Struct:
        def __init__(self):
            self.layer_list = []
            self.selected_layer_index_list = []

    class Layer_Backup_Struct:
        def __init__(self):
            self.layer_type_enum = None

            self.image           = None
            self.offset          = None

            self.name            = None
            self.hide_flag       = None
            self.lock_flag       = None
            self.mod_enum        = None
            self.opacity         = None

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

            layer_list = frame.Get_layer_list()
            for layer in layer_list:
                layer_backup                 = Backup_Controller.Layer_Backup_Struct()
                layer_backup.layer_type_enum = layer.layer_type_enum
                layer_backup.image           = layer.image.copy()
                layer_backup.offset          = layer.offset
                layer_backup.name            = layer.name
                layer_backup.hide_flag       = layer.hide_flag
                layer_backup.lock_flag       = layer.lock_flag
                layer_backup.mod_enum        = layer.mod_enum
                layer_backup.opacity         = layer.opacity

                frame_backup.layer_list.append(layer_backup)

            for selected_layer in frame.Get_selected_layer_list():
                index = layer_list.index(selected_layer)
                frame_backup.selected_layer_index_list.append(index)

            snapshot_backup.frame_list.append(frame_backup)

        return snapshot_backup

    def Revert_backup_snapshot(self, snapshot):
        frame_list = []

        for frame_backup in snapshot.frame_list:
            frame = Frame_Controller.Frame(self.frame_controller)

            for layer_backup in frame_backup.layer_list:
                if layer_backup.layer_type_enum == 'bit_layer':
                    layer = Board_Layer_Controller.Bit_Layer(controller = self.board_layer_controller,
                                                             widget     = self.board_layer_view.Yield_layer_widget(),
                                                             image      = layer_backup.image,
                                                             offset     = layer_backup.offset,   name    = layer_backup.name,
                                                             mod_enum   = layer_backup.mod_enum, opacity = layer_backup.opacity,)
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


    def On_revoke_action_triggered(self):
        self.Revoke_backup()

    def On_redo_action_triggered(self):
        self.Redo_backup()


class Style_Manage_Controller:
    def __init__(self, main_window):
        self.main_window = main_window

        self.base_color            = QColor(240, 240, 240)
        self.board_color           = QColor(160 ,160, 160)
        self.text_color            = QColor(0, 0, 0)
        self.highlight_back_color     = QColor(176, 176, 176)
        self.highlight_front_color    = QColor(255, 255, 255)
        self.weak_selected_color   = QColor(189, 242, 255)
        self.strong_selected_color = QColor(219, 219, 255)

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

        self.main_window.Layer_Name_LineEdit.textChanged.connect(self.board_layer_view.On_layer_name_lineedit_text_changed)
        self.main_window.Mix_Mod_ComboBox.currentTextChanged.connect(self.board_layer_view.On_mix_mod_combobox_text_changed)
        self.main_window.Opacity_Slider.value_change_single.connect(self.board_layer_view.On_opacity_slider_value_change)

        self.main_window.Board_H_ScrollBar.valueChanged.connect(self.board_layer_view.On_Board_h_scrollbar_value_changed)
        self.main_window.Board_V_ScrollBar.valueChanged.connect(self.board_layer_view.On_Board_v_scrollbar_value_changed)

        self.main_window.Rect_Selection_Button.clicked.connect(self.tool_view.On_rect_selection_button_clicked)
        self.main_window.Pencil_Button.clicked.connect(self.tool_view.On_pencil_button_clicked)

        self.main_window.Revoke_Action.triggered.connect(self.backup_controller.On_revoke_action_triggered)
        self.main_window.Redo_Action.triggered.connect(self.backup_controller.On_redo_action_triggered)
        self.main_window.New_Bit_Layer_Action.triggered.connect(self.board_layer_view.On_new_bit_layer_action_triggered)
        self.main_window.Cancel_Selection_Action.triggered.connect(self.board_layer_view.On_cancel_selection_action_triggered)
        self.main_window.Copy_Selection_Action.triggered.connect(self.board_layer_view.On_copy_selection_action_triggered)
        self.main_window.Cut_Selection_Action.triggered.connect(self.board_layer_view.On_cut_selection_action_triggered)


class Main_Window(QMainWindow, Ui_Main_Window_UI):
    def __init__(self):
        super().__init__()

        self.main_window = self

        self.image_edited_flag      = False
        self.key_space_pressed_flag = False
        self.key_ctrl_pressed_flag  = False

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

        self.frame_controller.New_project()

    def init(self):
        self.main_window.Board_Label.setFocus()

        self.main_window.Pencil_Size_ComboBox.setStyleSheet('''#Pencil_Size_ComboBox QAbstractItemView{min-width: 60px;}''')
        self.main_window.Board_Label_Widget.setStyleSheet('''#Board_Label_Widget{border:1px solid red}''')

        self.Color_Indicator_Widget = Color_Indicator_Widget(self)
        self.main_window.Quick_Func_Layout.addWidget(self.Color_Indicator_Widget, 0, 5, 2, 1, Qt.AlignHCenter)

        self.main_window.Opacity_Slider.Set_min_value(0)
        self.main_window.Opacity_Slider.Set_max_value(100)
        self.main_window.Opacity_Slider.Set_left_text('')

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

    def Main_window_key_release_event(self, event):
        if event.key() == Qt.Key_Space:
            self.Set_key_space_pressed_flag(False)
        elif event.key() == Qt.Key_Control:
            self.Set_key_ctrl_pressed_flag(False)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Main_Window()
    sys.exit(app.exec_())
