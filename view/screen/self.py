# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'self.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ScreenWindow(object):
    def setupUi(self, ScreenWindow):
        ScreenWindow.setObjectName("ScreenWindow")
        ScreenWindow.resize(641, 441)
        self.centralwidget = QtWidgets.QWidget(ScreenWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 639, 439))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.w_screen = QtWidgets.QWidget(self.scrollAreaWidgetContents)
        self.w_screen.setObjectName("w_screen")
        self.gridLayout_2.addWidget(self.w_screen, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        ScreenWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(ScreenWindow)
        QtCore.QMetaObject.connectSlotsByName(ScreenWindow)

    def retranslateUi(self, ScreenWindow):
        _translate = QtCore.QCoreApplication.translate
        ScreenWindow.setWindowTitle(_translate("ScreenWindow", "ScreenWindow"))

