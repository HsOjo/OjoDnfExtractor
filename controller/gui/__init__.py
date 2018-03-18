import sys

from PyQt5.QtWidgets import QApplication
from .main import MainWindow

from controller.gui.screen import ScreenWindow


class GUI:
    def __init__(self, args):
        self.args = args
        self.qt = QApplication(sys.argv)

        self.screen = ScreenWindow()
        self._event = {
            'set_texture': self.screen.set_texture,
            'set_canvas': self.screen.set_canvas,
        }

        self.main = MainWindow(self._event)
        self.main.open_file('img', 'test', './data/test.img')
        self.main.open_file('npk', 'sprite_interface2_cs_shop', './data/sprite_interface2_cs_shop.NPK')

    def start(self):
        self.screen.show()
        self.main.show()
        return self.qt.exec_()
