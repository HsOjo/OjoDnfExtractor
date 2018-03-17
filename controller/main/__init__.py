import os

from PyQt5.QtWidgets import QMainWindow, QFileDialog

from view.main.self import Ui_MainWindow
from .img_widget import IMGWidget
from .npk_widget import NPKWidget


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self, upper_event):
        super().__init__()
        self.setupUi(self)

        self._extract_dir = None
        self._extract_mode = None

        self._upper_event = upper_event
        self._event = {
            'set_texture': upper_event['set_texture'],
            'set_canvas': upper_event['set_canvas'],
            'open_file': self.open_file,
            'get_extract_dir': self.get_extract_dir,
            'get_extract_mode': lambda: self._extract_mode,
        }

        self.tab_widgets = []
        self.current_widget = None

        self.a_open.triggered.connect(self._a_open_triggered)
        self.a_close.triggered.connect(self._a_close_triggered)
        self.a_load_img.triggered.connect(self._a_load_img_triggered)
        self.a_sound_play.triggered.connect(self._a_sound_play_triggered)
        self.a_sound_pause.triggered.connect(self._a_sound_pause_triggered)
        self.a_sound_stop.triggered.connect(self._a_sound_stop_triggered)
        self.a_extract_dir.triggered.connect(lambda: self.set_extract_dir())
        self.a_extract_npk.triggered.connect(self._a_extract_npk_triggered)
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
        [path, type] = QFileDialog.getOpenFileName(parent=self, caption='打开文件', directory='./',
                                                   filter='NPK 文件(*.npk);;IMG 文件(*.img);;所有文件(*)')
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
            cw.play_current_sound(self.a_sound_loop.isChecked())

    def _a_sound_pause_triggered(self):
        cw = self.current_widget
        if isinstance(cw, NPKWidget):
            cw.pause_current_sound()

    def _a_sound_stop_triggered(self):
        cw = self.current_widget
        if isinstance(cw, NPKWidget):
            cw.stop_current_sound()

    def _a_extract_npk_triggered(self):
        cw = self.current_widget
        if isinstance(cw, NPKWidget):
            cw.extract_current_file()

    def set_extract_dir(self):
        dirname = QFileDialog.getExistingDirectory(parent=self, caption='选择提取目录', directory='./')
        if dirname != '':
            self._extract_dir = dirname

    def get_extract_dir(self):
        if self._extract_dir is None:
            self.set_extract_dir()

        return self._extract_dir
