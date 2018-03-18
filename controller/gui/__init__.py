import sys

from PyQt5.QtWidgets import QApplication

from controller.gui.screen import ScreenWindow
from .main import MainWindow


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

    def start(self):
        self.screen.show()
        self.main.show()
        return self.qt.exec_()
