# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'f:\Code\软件实训\Custom_Widgets\Layer_Widget_UI.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Layer_Widget_UI(object):
    def setupUi(self, Layer_Widget_UI):
        Layer_Widget_UI.setObjectName("Layer_Widget_UI")
        Layer_Widget_UI.resize(400, 78)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Layer_Widget_UI)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Visible_Button = QtWidgets.QPushButton(Layer_Widget_UI)
        self.Visible_Button.setMinimumSize(QtCore.QSize(20, 20))
        self.Visible_Button.setMaximumSize(QtCore.QSize(20, 20))
        self.Visible_Button.setObjectName("Visible_Button")
        self.verticalLayout_2.addWidget(self.Visible_Button)
        self.Lock_Button = QtWidgets.QPushButton(Layer_Widget_UI)
        self.Lock_Button.setMinimumSize(QtCore.QSize(20, 20))
        self.Lock_Button.setMaximumSize(QtCore.QSize(20, 20))
        self.Lock_Button.setObjectName("Lock_Button")
        self.verticalLayout_2.addWidget(self.Lock_Button)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.Preview_Label = QtWidgets.QLabel(Layer_Widget_UI)
        self.Preview_Label.setMinimumSize(QtCore.QSize(60, 60))
        self.Preview_Label.setMaximumSize(QtCore.QSize(60, 60))
        self.Preview_Label.setObjectName("Preview_Label")
        self.horizontalLayout.addWidget(self.Preview_Label)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.Layer_Name_Label = QtWidgets.QLabel(Layer_Widget_UI)
        self.Layer_Name_Label.setObjectName("Layer_Name_Label")
        self.verticalLayout.addWidget(self.Layer_Name_Label)
        self.Layer_Mod_Label = QtWidgets.QLabel(Layer_Widget_UI)
        self.Layer_Mod_Label.setObjectName("Layer_Mod_Label")
        self.verticalLayout.addWidget(self.Layer_Mod_Label)
        self.Layer_Opacity_Label = QtWidgets.QLabel(Layer_Widget_UI)
        self.Layer_Opacity_Label.setObjectName("Layer_Opacity_Label")
        self.verticalLayout.addWidget(self.Layer_Opacity_Label)
        self.horizontalLayout.addLayout(self.verticalLayout)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.retranslateUi(Layer_Widget_UI)
        QtCore.QMetaObject.connectSlotsByName(Layer_Widget_UI)

    def retranslateUi(self, Layer_Widget_UI):
        _translate = QtCore.QCoreApplication.translate
        self.Visible_Button.setText(_translate("Layer_Widget_UI", "见"))
        self.Lock_Button.setText(_translate("Layer_Widget_UI", "锁"))
        self.Preview_Label.setText(_translate("Layer_Widget_UI", "预览"))
        self.Layer_Name_Label.setText(_translate("Layer_Widget_UI", "名"))
        self.Layer_Mod_Label.setText(_translate("Layer_Widget_UI", "模式"))
        self.Layer_Opacity_Label.setText(_translate("Layer_Widget_UI", "不透明度"))
