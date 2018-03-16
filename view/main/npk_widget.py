# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'npk_widget.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NPKWidget(object):
    def setupUi(self, NPKWidget):
        NPKWidget.setObjectName("NPKWidget")
        NPKWidget.resize(588, 356)
        self.gridLayout_3 = QtWidgets.QGridLayout(NPKWidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox_2 = QtWidgets.QGroupBox(NPKWidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.tw_files = QtWidgets.QTableWidget(self.groupBox_2)
        self.tw_files.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tw_files.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tw_files.setObjectName("tw_files")
        self.tw_files.setColumnCount(3)
        self.tw_files.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tw_files.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tw_files.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tw_files.setHorizontalHeaderItem(2, item)
        self.tw_files.horizontalHeader().setDefaultSectionSize(80)
        self.tw_files.horizontalHeader().setStretchLastSection(True)
        self.tw_files.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tw_files, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_2, 0, 0, 2, 1)

        self.retranslateUi(NPKWidget)
        QtCore.QMetaObject.connectSlotsByName(NPKWidget)

    def retranslateUi(self, NPKWidget):
        _translate = QtCore.QCoreApplication.translate
        NPKWidget.setWindowTitle(_translate("NPKWidget", "NPK_Widget"))
        self.groupBox_2.setTitle(_translate("NPKWidget", "文件列表"))
        item = self.tw_files.horizontalHeaderItem(0)
        item.setText(_translate("NPKWidget", "索引"))
        item = self.tw_files.horizontalHeaderItem(1)
        item.setText(_translate("NPKWidget", "文件尺寸"))
        item = self.tw_files.horizontalHeaderItem(2)
        item.setText(_translate("NPKWidget", "文件名"))

