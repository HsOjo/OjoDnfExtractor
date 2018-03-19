import sys
import traceback
from io import StringIO

from PyQt5.QtWidgets import QApplication, QMessageBox

from controller.gui.screen import ScreenWindow
from util.io_helper import IOHelper
from .main import MainWindow


class GUI:
    def __init__(self, args):
        self.args = args
        self.qt = QApplication(sys.argv)
        sys.excepthook = GUI.print_exception

        self.screen = ScreenWindow()
        self._event = {
            'set_texture': self.screen.set_texture,
            'set_canvas': self.screen.set_canvas,
        }

        self.main = MainWindow(self._event)

    def start(self):
        self.screen.show()
        self.main.show()
        code = self.qt.exec_()
        return code

    @staticmethod
    def print_exception(type, value, tb):
        with StringIO() as io:
            traceback.print_exception(type, value, tb, file=io)
            err_str = IOHelper.read_range(io)
        QMessageBox.information(None, None, err_str)
