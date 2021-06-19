# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'f:\Code\软件实训\Custom_Widgets\Color_Picker\Color_Picker_Widget_UI.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Color_Picker_Widget_UI(object):
    def setupUi(self, Color_Picker_Widget_UI):
        Color_Picker_Widget_UI.setObjectName("Color_Picker_Widget_UI")
        Color_Picker_Widget_UI.resize(425, 562)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Color_Picker_Widget_UI.sizePolicy().hasHeightForWidth())
        Color_Picker_Widget_UI.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Color_Picker_Widget_UI)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Main_Layout = QtWidgets.QVBoxLayout()
        self.Main_Layout.setSpacing(6)
        self.Main_Layout.setObjectName("Main_Layout")
        self.Display_Button_Layout = QtWidgets.QHBoxLayout()
        self.Display_Button_Layout.setObjectName("Display_Button_Layout")
        self.Color_Wheel_Button = QtWidgets.QPushButton(Color_Picker_Widget_UI)
        self.Color_Wheel_Button.setMinimumSize(QtCore.QSize(28, 28))
        self.Color_Wheel_Button.setMaximumSize(QtCore.QSize(28, 28))
        self.Color_Wheel_Button.setObjectName("Color_Wheel_Button")
        self.Display_Button_Layout.addWidget(self.Color_Wheel_Button)
        self.RGB_Button = QtWidgets.QPushButton(Color_Picker_Widget_UI)
        self.RGB_Button.setMinimumSize(QtCore.QSize(28, 28))
        self.RGB_Button.setMaximumSize(QtCore.QSize(28, 28))
        self.RGB_Button.setObjectName("RGB_Button")
        self.Display_Button_Layout.addWidget(self.RGB_Button)
        self.HSV_Button = QtWidgets.QPushButton(Color_Picker_Widget_UI)
        self.HSV_Button.setMinimumSize(QtCore.QSize(28, 28))
        self.HSV_Button.setMaximumSize(QtCore.QSize(28, 28))
        self.HSV_Button.setObjectName("HSV_Button")
        self.Display_Button_Layout.addWidget(self.HSV_Button)
        self.Swatches_Button = QtWidgets.QPushButton(Color_Picker_Widget_UI)
        self.Swatches_Button.setMinimumSize(QtCore.QSize(28, 28))
        self.Swatches_Button.setMaximumSize(QtCore.QSize(28, 28))
        self.Swatches_Button.setObjectName("Swatches_Button")
        self.Display_Button_Layout.addWidget(self.Swatches_Button)
        spacerItem = QtWidgets.QSpacerItem(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.Display_Button_Layout.addItem(spacerItem)
        self.Display_Button_Layout.setStretch(4, 1)
        self.Main_Layout.addLayout(self.Display_Button_Layout)
        self.Color_Wheel_Widget = Color_Wheel(Color_Picker_Widget_UI)
        self.Color_Wheel_Widget.setMinimumSize(QtCore.QSize(200, 200))
        self.Color_Wheel_Widget.setObjectName("Color_Wheel_Widget")
        self.Main_Layout.addWidget(self.Color_Wheel_Widget)
        self.RGB_Layout = QtWidgets.QWidget(Color_Picker_Widget_UI)
        self.RGB_Layout.setObjectName("RGB_Layout")
        self.RGB_Layout_2 = QtWidgets.QVBoxLayout(self.RGB_Layout)
        self.RGB_Layout_2.setContentsMargins(0, 0, 0, 0)
        self.RGB_Layout_2.setSpacing(4)
        self.RGB_Layout_2.setObjectName("RGB_Layout_2")
        self.line = QtWidgets.QFrame(self.RGB_Layout)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.RGB_Layout_2.addWidget(self.line)
        self.R_Layout = QtWidgets.QHBoxLayout()
        self.R_Layout.setObjectName("R_Layout")
        self.R_Label = QtWidgets.QLabel(self.RGB_Layout)
        self.R_Label.setObjectName("R_Label")
        self.R_Layout.addWidget(self.R_Label)
        self.R_LineEdit = QtWidgets.QLineEdit(self.RGB_Layout)
        self.R_LineEdit.setMinimumSize(QtCore.QSize(40, 0))
        self.R_LineEdit.setMaximumSize(QtCore.QSize(40, 16777215))
        self.R_LineEdit.setObjectName("R_LineEdit")
        self.R_Layout.addWidget(self.R_LineEdit)
        self.R_Slider = Color_Slider(self.RGB_Layout)
        self.R_Slider.setMinimumSize(QtCore.QSize(0, 34))
        self.R_Slider.setMaximumSize(QtCore.QSize(16777215, 34))
        self.R_Slider.setObjectName("R_Slider")
        self.R_Layout.addWidget(self.R_Slider)
        self.R_Layout.setStretch(2, 1)
        self.RGB_Layout_2.addLayout(self.R_Layout)
        self.G_Layout = QtWidgets.QHBoxLayout()
        self.G_Layout.setObjectName("G_Layout")
        self.G_Label = QtWidgets.QLabel(self.RGB_Layout)
        self.G_Label.setObjectName("G_Label")
        self.G_Layout.addWidget(self.G_Label)
        self.G_LineEdit = QtWidgets.QLineEdit(self.RGB_Layout)
        self.G_LineEdit.setMinimumSize(QtCore.QSize(40, 0))
        self.G_LineEdit.setMaximumSize(QtCore.QSize(40, 16777215))
        self.G_LineEdit.setObjectName("G_LineEdit")
        self.G_Layout.addWidget(self.G_LineEdit)
        self.G_Slider = Color_Slider(self.RGB_Layout)
        self.G_Slider.setMinimumSize(QtCore.QSize(0, 34))
        self.G_Slider.setMaximumSize(QtCore.QSize(16777215, 34))
        self.G_Slider.setObjectName("G_Slider")
        self.G_Layout.addWidget(self.G_Slider)
        self.G_Layout.setStretch(2, 1)
        self.RGB_Layout_2.addLayout(self.G_Layout)
        self.B_Layout = QtWidgets.QHBoxLayout()
        self.B_Layout.setObjectName("B_Layout")
        self.B_Label = QtWidgets.QLabel(self.RGB_Layout)
        self.B_Label.setObjectName("B_Label")
        self.B_Layout.addWidget(self.B_Label)
        self.B_LineEdit = QtWidgets.QLineEdit(self.RGB_Layout)
        self.B_LineEdit.setMinimumSize(QtCore.QSize(40, 0))
        self.B_LineEdit.setMaximumSize(QtCore.QSize(40, 16777215))
        self.B_LineEdit.setObjectName("B_LineEdit")
        self.B_Layout.addWidget(self.B_LineEdit)
        self.B_Slider = Color_Slider(self.RGB_Layout)
        self.B_Slider.setMinimumSize(QtCore.QSize(0, 34))
        self.B_Slider.setMaximumSize(QtCore.QSize(16777215, 34))
        self.B_Slider.setObjectName("B_Slider")
        self.B_Layout.addWidget(self.B_Slider)
        self.B_Layout.setStretch(2, 1)
        self.RGB_Layout_2.addLayout(self.B_Layout)
        self.Main_Layout.addWidget(self.RGB_Layout)
        self.HSV_Layout = QtWidgets.QWidget(Color_Picker_Widget_UI)
        self.HSV_Layout.setObjectName("HSV_Layout")
        self.HSV_Layout_2 = QtWidgets.QVBoxLayout(self.HSV_Layout)
        self.HSV_Layout_2.setContentsMargins(0, 0, 0, 0)
        self.HSV_Layout_2.setSpacing(4)
        self.HSV_Layout_2.setObjectName("HSV_Layout_2")
        self.line_2 = QtWidgets.QFrame(self.HSV_Layout)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.HSV_Layout_2.addWidget(self.line_2)
        self.H_Layout = QtWidgets.QHBoxLayout()
        self.H_Layout.setObjectName("H_Layout")
        self.H_Label = QtWidgets.QLabel(self.HSV_Layout)
        self.H_Label.setObjectName("H_Label")
        self.H_Layout.addWidget(self.H_Label)
        self.H_LineEdit = QtWidgets.QLineEdit(self.HSV_Layout)
        self.H_LineEdit.setMinimumSize(QtCore.QSize(40, 0))
        self.H_LineEdit.setMaximumSize(QtCore.QSize(40, 16777215))
        self.H_LineEdit.setObjectName("H_LineEdit")
        self.H_Layout.addWidget(self.H_LineEdit)
        self.H_Slider = Color_Slider(self.HSV_Layout)
        self.H_Slider.setMinimumSize(QtCore.QSize(0, 34))
        self.H_Slider.setMaximumSize(QtCore.QSize(16777215, 34))
        self.H_Slider.setObjectName("H_Slider")
        self.H_Layout.addWidget(self.H_Slider)
        self.H_Layout.setStretch(2, 1)
        self.HSV_Layout_2.addLayout(self.H_Layout)
        self.S_Layout = QtWidgets.QHBoxLayout()
        self.S_Layout.setObjectName("S_Layout")
        self.S_Label = QtWidgets.QLabel(self.HSV_Layout)
        self.S_Label.setObjectName("S_Label")
        self.S_Layout.addWidget(self.S_Label)
        self.S_LineEdit = QtWidgets.QLineEdit(self.HSV_Layout)
        self.S_LineEdit.setMinimumSize(QtCore.QSize(40, 0))
        self.S_LineEdit.setMaximumSize(QtCore.QSize(40, 16777215))
        self.S_LineEdit.setObjectName("S_LineEdit")
        self.S_Layout.addWidget(self.S_LineEdit)
        self.S_Slider = Color_Slider(self.HSV_Layout)
        self.S_Slider.setMinimumSize(QtCore.QSize(0, 34))
        self.S_Slider.setMaximumSize(QtCore.QSize(16777215, 34))
        self.S_Slider.setObjectName("S_Slider")
        self.S_Layout.addWidget(self.S_Slider)
        self.S_Layout.setStretch(2, 1)
        self.HSV_Layout_2.addLayout(self.S_Layout)
        self.V_Layout = QtWidgets.QHBoxLayout()
        self.V_Layout.setObjectName("V_Layout")
        self.V_Label = QtWidgets.QLabel(self.HSV_Layout)
        self.V_Label.setObjectName("V_Label")
        self.V_Layout.addWidget(self.V_Label)
        self.V_LineEdit = QtWidgets.QLineEdit(self.HSV_Layout)
        self.V_LineEdit.setMinimumSize(QtCore.QSize(40, 0))
        self.V_LineEdit.setMaximumSize(QtCore.QSize(40, 16777215))
        self.V_LineEdit.setObjectName("V_LineEdit")
        self.V_Layout.addWidget(self.V_LineEdit)
        self.V_Slider = Color_Slider(self.HSV_Layout)
        self.V_Slider.setMinimumSize(QtCore.QSize(0, 34))
        self.V_Slider.setMaximumSize(QtCore.QSize(16777215, 34))
        self.V_Slider.setObjectName("V_Slider")
        self.V_Layout.addWidget(self.V_Slider)
        self.V_Layout.setStretch(2, 1)
        self.HSV_Layout_2.addLayout(self.V_Layout)
        self.Main_Layout.addWidget(self.HSV_Layout)
        self.verticalLayout_2.addLayout(self.Main_Layout)

        self.retranslateUi(Color_Picker_Widget_UI)
        QtCore.QMetaObject.connectSlotsByName(Color_Picker_Widget_UI)

    def retranslateUi(self, Color_Picker_Widget_UI):
        _translate = QtCore.QCoreApplication.translate
        self.Color_Wheel_Button.setText(_translate("Color_Picker_Widget_UI", "色轮"))
        self.RGB_Button.setText(_translate("Color_Picker_Widget_UI", "RGB"))
        self.HSV_Button.setText(_translate("Color_Picker_Widget_UI", "HSV"))
        self.Swatches_Button.setText(_translate("Color_Picker_Widget_UI", "常用"))
        self.R_Label.setText(_translate("Color_Picker_Widget_UI", "R"))
        self.R_LineEdit.setInputMask(_translate("Color_Picker_Widget_UI", "D00"))
        self.R_LineEdit.setText(_translate("Color_Picker_Widget_UI", "0"))
        self.G_Label.setText(_translate("Color_Picker_Widget_UI", "G"))
        self.G_LineEdit.setInputMask(_translate("Color_Picker_Widget_UI", "D00"))
        self.G_LineEdit.setText(_translate("Color_Picker_Widget_UI", "0"))
        self.B_Label.setText(_translate("Color_Picker_Widget_UI", "B"))
        self.B_LineEdit.setInputMask(_translate("Color_Picker_Widget_UI", "D00"))
        self.B_LineEdit.setText(_translate("Color_Picker_Widget_UI", "0"))
        self.H_Label.setText(_translate("Color_Picker_Widget_UI", "H"))
        self.H_LineEdit.setInputMask(_translate("Color_Picker_Widget_UI", "D00"))
        self.H_LineEdit.setText(_translate("Color_Picker_Widget_UI", "0"))
        self.S_Label.setText(_translate("Color_Picker_Widget_UI", "S"))
        self.S_LineEdit.setInputMask(_translate("Color_Picker_Widget_UI", "D00"))
        self.S_LineEdit.setText(_translate("Color_Picker_Widget_UI", "0"))
        self.V_Label.setText(_translate("Color_Picker_Widget_UI", "V"))
        self.V_LineEdit.setInputMask(_translate("Color_Picker_Widget_UI", "D00"))
        self.V_LineEdit.setText(_translate("Color_Picker_Widget_UI", "0"))
from .Color_Slider import Color_Slider
from .Color_Wheel import Color_Wheel
