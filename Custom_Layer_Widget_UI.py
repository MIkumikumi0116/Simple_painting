# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'f:\Code\软件实训\Custom_Layer_Widget_UI.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Custom_Layer_Widget_UI(object):
    def setupUi(self, Custom_Layer_Widget_UI):
        Custom_Layer_Widget_UI.setObjectName("Custom_Layer_Widget_UI")
        Custom_Layer_Widget_UI.resize(400, 77)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Custom_Layer_Widget_UI)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Layer_widget_button_layout_1 = QtWidgets.QVBoxLayout()
        self.Layer_widget_button_layout_1.setObjectName("Layer_widget_button_layout_1")
        self.Layer_widget_visible_button1 = QtWidgets.QPushButton(Custom_Layer_Widget_UI)
        self.Layer_widget_visible_button1.setMinimumSize(QtCore.QSize(20, 20))
        self.Layer_widget_visible_button1.setMaximumSize(QtCore.QSize(20, 20))
        self.Layer_widget_visible_button1.setObjectName("Layer_widget_visible_button1")
        self.Layer_widget_button_layout_1.addWidget(self.Layer_widget_visible_button1)
        self.Layer_widget_lock_button1 = QtWidgets.QPushButton(Custom_Layer_Widget_UI)
        self.Layer_widget_lock_button1.setMinimumSize(QtCore.QSize(20, 20))
        self.Layer_widget_lock_button1.setMaximumSize(QtCore.QSize(20, 20))
        self.Layer_widget_lock_button1.setObjectName("Layer_widget_lock_button1")
        self.Layer_widget_button_layout_1.addWidget(self.Layer_widget_lock_button1)
        self.horizontalLayout.addLayout(self.Layer_widget_button_layout_1)
        self.Layer_widget_preview_label_1 = QtWidgets.QLabel(Custom_Layer_Widget_UI)
        self.Layer_widget_preview_label_1.setObjectName("Layer_widget_preview_label_1")
        self.horizontalLayout.addWidget(self.Layer_widget_preview_label_1)
        self.verticalLayout_24 = QtWidgets.QVBoxLayout()
        self.verticalLayout_24.setObjectName("verticalLayout_24")
        self.Layer_widget_layer_name_1 = QtWidgets.QLabel(Custom_Layer_Widget_UI)
        self.Layer_widget_layer_name_1.setObjectName("Layer_widget_layer_name_1")
        self.verticalLayout_24.addWidget(self.Layer_widget_layer_name_1)
        self.Layer_widget_layer_mod_1 = QtWidgets.QLabel(Custom_Layer_Widget_UI)
        self.Layer_widget_layer_mod_1.setObjectName("Layer_widget_layer_mod_1")
        self.verticalLayout_24.addWidget(self.Layer_widget_layer_mod_1)
        self.Layer_widget_layer_Opacity_1 = QtWidgets.QLabel(Custom_Layer_Widget_UI)
        self.Layer_widget_layer_Opacity_1.setObjectName("Layer_widget_layer_Opacity_1")
        self.verticalLayout_24.addWidget(self.Layer_widget_layer_Opacity_1)
        self.horizontalLayout.addLayout(self.verticalLayout_24)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.retranslateUi(Custom_Layer_Widget_UI)
        QtCore.QMetaObject.connectSlotsByName(Custom_Layer_Widget_UI)

    def retranslateUi(self, Custom_Layer_Widget_UI):
        _translate = QtCore.QCoreApplication.translate
        Custom_Layer_Widget_UI.setWindowTitle(_translate("Custom_Layer_Widget_UI", "Form"))
        self.Layer_widget_visible_button1.setText(_translate("Custom_Layer_Widget_UI", "见"))
        self.Layer_widget_lock_button1.setText(_translate("Custom_Layer_Widget_UI", "锁"))
        self.Layer_widget_preview_label_1.setText(_translate("Custom_Layer_Widget_UI", "预览"))
        self.Layer_widget_layer_name_1.setText(_translate("Custom_Layer_Widget_UI", "名"))
        self.Layer_widget_layer_mod_1.setText(_translate("Custom_Layer_Widget_UI", "模式"))
        self.Layer_widget_layer_Opacity_1.setText(_translate("Custom_Layer_Widget_UI", "不透明度"))
