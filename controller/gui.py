import sys

from PyQt5.QtWidgets import QApplication

from controller.main import MainWindow
from controller.screen import ScreenWindow


class GUI:
    def __init__(self, args):
        self.args = args
        self.qt = QApplication(sys.argv)
        self.main = MainWindow()
        self.screen = ScreenWindow()
        self.main.open_file('img', 'test', './data/test.img')
        self.main.open_file('npk', 'sprite_interface2_cs_shop', './data/sprite_interface2_cs_shop.NPK')

    def start(self):
        self.main.show()
        # self.screen.show()
        return self.qt.exec_()
