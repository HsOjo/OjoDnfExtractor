from PyQt5.QtWidgets import QMainWindow

from view.screen.self import Ui_ScreenWindow


class ScreenWindow(Ui_ScreenWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

