import os

from PyQt5.QtWidgets import QMainWindow, QFileDialog

from view.main.self import Ui_MainWindow
from .img_widget import IMGWidget
from .npk_widget import NPKWidget


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, upper_event):
        super().__init__()
        self.setupUi(self)

        self._upper_event = upper_event
        self._event = {
            'set_texture': upper_event['set_texture'],
            'set_canvas': upper_event['set_canvas'],
            'open_file': self.open_file,
        }

        self.tab_widgets = []
        self.current_widget = None

        self.a_open.triggered.connect(self._a_open_triggered)
        self.a_close.triggered.connect(self._a_close_triggered)
        self.a_load_img.triggered.connect(self._a_load_img_triggered)
        self.a_sound_play.triggered.connect(self._a_sound_play_triggered)
        self.a_sound_pause.triggered.connect(self._a_sound_pause_triggered)
        self.a_sound_stop.triggered.connect(self._a_sound_stop_triggered)
        self.a_sound_loop.triggered.connect(self._a_sound_loop_triggered)
        self.tw_content.currentChanged.connect(self._tw_content_current_changed)

    def add_tab_widget(self, name, widget):
        self.tab_widgets.append(widget)
        self.tw_content.addTab(widget, name)

    def open_file(self, type, name, path):
        if type == 'npk':
            self.add_tab_widget(name, NPKWidget(path, self._event))
        elif type == 'img':
            self.add_tab_widget(name, IMGWidget(path, self._event))

    def _a_open_triggered(self):
        [path, type] = QFileDialog.getOpenFileName(parent=self, caption='Open File', directory='./',
                                                   filter='NPK Files(*.npk);;IMG Files(*.img);;All Files(*)')
        if os.path.exists(path):
            [dir, file] = os.path.split(path)
            if file[-4:].lower() == '.npk':
                self.open_file('npk', file, path)
            elif file[-4:].lower() == '.img':
                self.open_file('img', file, path)

    def _a_close_triggered(self):
        if self.current_widget is not None:
            self.tab_widgets.remove(self.current_widget)
            self.current_widget = None
            self.tw_content.removeTab(self.tw_content.currentIndex())
        else:
            self.close()

    def _a_load_img_triggered(self):
        cw = self.current_widget
        if isinstance(cw, NPKWidget):
            cw.load_current_img()

    def _tw_content_current_changed(self, index):
        tws = self.tab_widgets
        if len(tws) > 0:
            self.current_widget = tws[index]

    def _a_sound_play_triggered(self):
        cw = self.current_widget
        if isinstance(cw, NPKWidget):
            cw.get_sound(cw.tw_files.currentRow()).play()

    def _a_sound_pause_triggered(self):
        cw = self.current_widget
        if isinstance(cw, NPKWidget):
            cw.get_sound(cw.tw_files.currentRow()).pause()

    def _a_sound_stop_triggered(self):
        cw = self.current_widget
        if isinstance(cw, NPKWidget):
            cw.get_sound(cw.tw_files.currentRow()).stop()

    def _a_sound_loop_triggered(self):
        cw = self.current_widget
        if isinstance(cw, NPKWidget):
            cw.get_sound(cw.tw_files.currentRow()).set_loop(self.a_sound_loop.isChecked())
