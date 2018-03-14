import sys

from PyQt5.QtWidgets import QApplication

from controller.main import MainWindow


class GUI:
    def __init__(self, args):
        self.args = args
        self.qt = QApplication(sys.argv)
        self.main = MainWindow()

    def start(self):
        self.main.show()
        return self.qt.exec_()
