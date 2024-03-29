import sys
import traceback
from io import StringIO

from PyQt6.QtWidgets import QApplication, QMessageBox

from app.screen import ScreenWindow
from app.util.io_helper import IOHelper
from .main import MainWindow
from app.libs.bass import Bass


class Application:
    def __init__(self, args):
        self.args = args
        self.qt = QApplication(sys.argv)
        sys.excepthook = Application.print_exception

        self.screen = ScreenWindow()
        self._event = {
            'set_texture': self.screen.set_texture,
            'set_canvas': self.screen.set_canvas,
            'process_events': self.qt.processEvents,
        }

        self.main = MainWindow(self._event)

    def start(self):
        self.screen.show()
        self.main.show()

        for file in self.args.files:
            self.main.open_file_auto(file)

        Bass.init()
        code = self.qt.exec()
        Bass.free()

        return code

    @staticmethod
    def print_exception(type, value, tb):
        with StringIO() as io:
            traceback.print_exception(type, value, tb, file=io)
            err_str = IOHelper.read_range(io)
        print(err_str)
        QMessageBox.warning(None, '错误：', err_str)
