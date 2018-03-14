from PyQt5.QtWidgets import QWidget

from view.main.img_widget import Ui_IMGWidget


class IMGWidget(Ui_IMGWidget, QWidget):
    def __init__(self, path):
        super().__init__()
        self.setupUi(self)
