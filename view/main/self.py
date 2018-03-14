# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'self.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tw_content = QtWidgets.QTabWidget(self.centralwidget)
        self.tw_content.setObjectName("tw_content")
        self.gridLayout.addWidget(self.tw_content, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setDefaultUp(False)
        self.menubar.setNativeMenuBar(True)
        self.menubar.setObjectName("menubar")
        self.menu_app = QtWidgets.QMenu(self.menubar)
        self.menu_app.setObjectName("menu_app")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.a_open = QtWidgets.QAction(MainWindow)
        self.a_open.setObjectName("a_open")
        self.menu_app.addAction(self.a_open)
        self.menubar.addAction(self.menu_app.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menu_app.setTitle(_translate("MainWindow", "文件"))
        self.a_open.setText(_translate("MainWindow", "打开"))
        self.a_open.setShortcut(_translate("MainWindow", "Ctrl+O"))

