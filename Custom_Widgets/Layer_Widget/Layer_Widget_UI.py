# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'f:\Code\软件实训\Custom_Widgets\Layer_Widget\Layer_Widget_UI.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Layer_Widget_UI(object):
    def setupUi(self, Layer_Widget_UI):
        Layer_Widget_UI.setObjectName("Layer_Widget_UI")
        self.horizontalLayout = QtWidgets.QHBoxLayout(Layer_Widget_UI)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Button_Layout = QtWidgets.QVBoxLayout()
        self.Button_Layout.setObjectName("Button_Layout")
        self.Hide_Button = QtWidgets.QPushButton(Layer_Widget_UI)
        self.Hide_Button.setMinimumSize(QtCore.QSize(20, 20))
        self.Hide_Button.setMaximumSize(QtCore.QSize(20, 20))
        self.Hide_Button.setCheckable(True)
        self.Hide_Button.setChecked(False)
        self.Hide_Button.setObjectName("Hide_Button")
        self.Button_Layout.addWidget(self.Hide_Button)
        self.Lock_Button = QtWidgets.QPushButton(Layer_Widget_UI)
        self.Lock_Button.setMinimumSize(QtCore.QSize(20, 20))
        self.Lock_Button.setMaximumSize(QtCore.QSize(20, 20))
        self.Lock_Button.setCheckable(True)
        self.Lock_Button.setObjectName("Lock_Button")
        self.Button_Layout.addWidget(self.Lock_Button)
        self.horizontalLayout.addLayout(self.Button_Layout)
        self.Preview_Label = QtWidgets.QLabel(Layer_Widget_UI)
        self.Preview_Label.setMinimumSize(QtCore.QSize(80, 80))
        self.Preview_Label.setMaximumSize(QtCore.QSize(80, 80))
        self.Preview_Label.setObjectName("Preview_Label")
        self.horizontalLayout.addWidget(self.Preview_Label)
        self.Attributes_Layout = QtWidgets.QVBoxLayout()
        self.Attributes_Layout.setObjectName("Attributes_Layout")
        self.Name_Label = QtWidgets.QLabel(Layer_Widget_UI)
        self.Name_Label.setObjectName("Name_Label")
        self.Attributes_Layout.addWidget(self.Name_Label)
        self.Mod_Label = QtWidgets.QLabel(Layer_Widget_UI)
        self.Mod_Label.setObjectName("Mod_Label")
        self.Attributes_Layout.addWidget(self.Mod_Label)
        self.Opacity_Label = QtWidgets.QLabel(Layer_Widget_UI)
        self.Opacity_Label.setObjectName("Opacity_Label")
        self.Attributes_Layout.addWidget(self.Opacity_Label)
        self.horizontalLayout.addLayout(self.Attributes_Layout)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.retranslateUi(Layer_Widget_UI)
        QtCore.QMetaObject.connectSlotsByName(Layer_Widget_UI)

    def retranslateUi(self, Layer_Widget_UI):
        _translate = QtCore.QCoreApplication.translate
        self.Hide_Button.setText(_translate("Layer_Widget_UI", "藏"))
        self.Lock_Button.setText(_translate("Layer_Widget_UI", "锁"))
        self.Preview_Label.setText(_translate("Layer_Widget_UI", "预览"))
        self.Name_Label.setText(_translate("Layer_Widget_UI", "名"))
        self.Mod_Label.setText(_translate("Layer_Widget_UI", "模式"))
        self.Opacity_Label.setText(_translate("Layer_Widget_UI", "不透明度"))
