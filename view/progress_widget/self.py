# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'self.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ProgressWidget(object):
    def setupUi(self, ProgressWidget):
        ProgressWidget.setObjectName("ProgressWidget")
        ProgressWidget.resize(256, 128)
        self.gridLayout_2 = QtWidgets.QGridLayout(ProgressWidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.pb_work = QtWidgets.QProgressBar(ProgressWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pb_work.sizePolicy().hasHeightForWidth())
        self.pb_work.setSizePolicy(sizePolicy)
        self.pb_work.setProperty("value", 24)
        self.pb_work.setObjectName("pb_work")
        self.gridLayout.addWidget(self.pb_work, 1, 0, 1, 1)
        self.l_progress = QtWidgets.QLabel(ProgressWidget)
        self.l_progress.setAlignment(QtCore.Qt.AlignCenter)
        self.l_progress.setObjectName("l_progress")
        self.gridLayout.addWidget(self.l_progress, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(ProgressWidget)
        QtCore.QMetaObject.connectSlotsByName(ProgressWidget)

    def retranslateUi(self, ProgressWidget):
        _translate = QtCore.QCoreApplication.translate
        ProgressWidget.setWindowTitle(_translate("ProgressWidget", "工作中..."))
        self.l_progress.setText(_translate("ProgressWidget", "Progress Text"))

