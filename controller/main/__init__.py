import os

from PyQt5.QtWidgets import QMainWindow, QFileDialog

from view.main.self import Ui_MainWindow
from .img_widget import IMGWidget
from .npk_widget import NPKWidget


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tab_widgets = []

        self.a_open.triggered.connect(self._a_open_triggered)

    def add_tab_widget(self, name, widget):
        self.tab_widgets.append(widget)
        self.tw_content.addTab(widget, name)

    def _a_open_triggered(self, b):
        [path, type] = QFileDialog.getOpenFileName(parent=self, caption='Open File', directory='./',
                                                   filter='NPK Files(*.npk);;IMG Files(*.img);;All Files(*)')
        if os.path.exists(path):
            [dir, file] = os.path.split(path)
            if file[-4:].lower() == '.npk':
                self.add_tab_widget(file, NPKWidget(path))
            elif file[-4:].lower() == '.img':
                self.add_tab_widget(file, IMGWidget(path))
