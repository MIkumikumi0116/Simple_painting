# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'f:\Code\软件实训\Custom_Dialog\New_Project_Dialog\New_Project_Dialog_UI.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_New_Project_Dialog_UI(object):
    def setupUi(self, New_Project_Dialog_UI):
        New_Project_Dialog_UI.setObjectName("New_Project_Dialog_UI")
        New_Project_Dialog_UI.resize(290, 175)
        self.verticalLayout = QtWidgets.QVBoxLayout(New_Project_Dialog_UI)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Preset_Size_Layout = QtWidgets.QHBoxLayout()
        self.Preset_Size_Layout.setObjectName("Preset_Size_Layout")
        self.Preset_Size_Label = QtWidgets.QLabel(New_Project_Dialog_UI)
        self.Preset_Size_Label.setObjectName("Preset_Size_Label")
        self.Preset_Size_Layout.addWidget(self.Preset_Size_Label)
        self.Preset_Size_ComboBox = QtWidgets.QComboBox(New_Project_Dialog_UI)
        self.Preset_Size_ComboBox.setMinimumSize(QtCore.QSize(110, 0))
        self.Preset_Size_ComboBox.setObjectName("Preset_Size_ComboBox")
        self.Preset_Size_ComboBox.addItem("")
        self.Preset_Size_ComboBox.addItem("")
        self.Preset_Size_ComboBox.addItem("")
        self.Preset_Size_ComboBox.addItem("")
        self.Preset_Size_ComboBox.addItem("")
        self.Preset_Size_ComboBox.addItem("")
        self.Preset_Size_Layout.addWidget(self.Preset_Size_ComboBox)
        self.verticalLayout_2.addLayout(self.Preset_Size_Layout)
        self.Width_Layout = QtWidgets.QHBoxLayout()
        self.Width_Layout.setObjectName("Width_Layout")
        self.Width_Label = QtWidgets.QLabel(New_Project_Dialog_UI)
        self.Width_Label.setObjectName("Width_Label")
        self.Width_Layout.addWidget(self.Width_Label)
        self.Width_LineEdit = QtWidgets.QLineEdit(New_Project_Dialog_UI)
        self.Width_LineEdit.setMinimumSize(QtCore.QSize(60, 0))
        self.Width_LineEdit.setMaximumSize(QtCore.QSize(60, 16777215))
        self.Width_LineEdit.setObjectName("Width_LineEdit")
        self.Width_Layout.addWidget(self.Width_LineEdit)
        self.verticalLayout_2.addLayout(self.Width_Layout)
        self.Height_Layout = QtWidgets.QHBoxLayout()
        self.Height_Layout.setObjectName("Height_Layout")
        self.Height_Label = QtWidgets.QLabel(New_Project_Dialog_UI)
        self.Height_Label.setObjectName("Height_Label")
        self.Height_Layout.addWidget(self.Height_Label)
        self.Height_LineEdit = QtWidgets.QLineEdit(New_Project_Dialog_UI)
        self.Height_LineEdit.setMinimumSize(QtCore.QSize(60, 0))
        self.Height_LineEdit.setMaximumSize(QtCore.QSize(60, 16777215))
        self.Height_LineEdit.setObjectName("Height_LineEdit")
        self.Height_Layout.addWidget(self.Height_LineEdit)
        self.verticalLayout_2.addLayout(self.Height_Layout)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.Confirm_Button = QtWidgets.QPushButton(New_Project_Dialog_UI)
        self.Confirm_Button.setObjectName("Confirm_Button")
        self.horizontalLayout.addWidget(self.Confirm_Button)
        self.Cancel_Button = QtWidgets.QPushButton(New_Project_Dialog_UI)
        self.Cancel_Button.setObjectName("Cancel_Button")
        self.horizontalLayout.addWidget(self.Cancel_Button)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(New_Project_Dialog_UI)
        QtCore.QMetaObject.connectSlotsByName(New_Project_Dialog_UI)

    def retranslateUi(self, New_Project_Dialog_UI):
        _translate = QtCore.QCoreApplication.translate
        New_Project_Dialog_UI.setWindowTitle(_translate("New_Project_Dialog_UI", "新建工程"))
        self.Preset_Size_Label.setText(_translate("New_Project_Dialog_UI", "预设尺寸"))
        self.Preset_Size_ComboBox.setItemText(0, _translate("New_Project_Dialog_UI", "1920×1080"))
        self.Preset_Size_ComboBox.setItemText(1, _translate("New_Project_Dialog_UI", "1024×1024"))
        self.Preset_Size_ComboBox.setItemText(2, _translate("New_Project_Dialog_UI", "1280×720"))
        self.Preset_Size_ComboBox.setItemText(3, _translate("New_Project_Dialog_UI", "512×512"))
        self.Preset_Size_ComboBox.setItemText(4, _translate("New_Project_Dialog_UI", "256×256"))
        self.Preset_Size_ComboBox.setItemText(5, _translate("New_Project_Dialog_UI", "64×64"))
        self.Width_Label.setText(_translate("New_Project_Dialog_UI", "宽度"))
        self.Width_LineEdit.setText(_translate("New_Project_Dialog_UI", "256"))
        self.Height_Label.setText(_translate("New_Project_Dialog_UI", "高度"))
        self.Height_LineEdit.setText(_translate("New_Project_Dialog_UI", "256"))
        self.Confirm_Button.setText(_translate("New_Project_Dialog_UI", "确定"))
        self.Cancel_Button.setText(_translate("New_Project_Dialog_UI", "取消"))
