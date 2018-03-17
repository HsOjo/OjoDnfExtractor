import os
from io import BytesIO

from PyQt5.QtWidgets import QWidget

from lib.bass import Bass
from model.npk import NPK
from util import common
from view.main.npk_widget import Ui_NPKWidget


class NPKWidget(Ui_NPKWidget, QWidget):
    def __init__(self, path, upper_event):
        super().__init__()
        self.setupUi(self)

        self._upper_event = upper_event

        if type(path) == bytes:
            io = BytesIO(path)
        elif type(path) == str:
            io = open(path, 'br+')
        else:
            raise Exception('Unsupport value type.')

        self._npk = NPK(io)
        self._sound = None
        self._sound_temp = {}

        self.refresh_files()

    def load_current_img(self):
        ue = self._upper_event
        npk = self._npk
        tw = self.tw_files
        row = tw.currentRow()
        info = npk.info(row)
        if info is not None:
            data = npk.load_file(row)
            [dirname, filename] = os.path.split(info['name'])

            ue['open_file']('img', filename, data)

    def refresh_files(self):
        tw = self.tw_files
        npk = self._npk

        row_count = tw.rowCount()
        file_count = len(npk.files)

        if row_count > file_count:
            for i in range(row_count - 1, file_count - 1, -1):
                tw.removeRow(i)
        else:
            for i in range(file_count - row_count):
                tw.insertRow(0)

        for i in npk.files:
            info = npk.info(i)
            tw.setItem(i, 0, common.qtwi_str(i))
            tw.setItem(i, 1, common.qtwi_str(info['size']))
            tw.setItem(i, 2, common.qtwi_str(info['name']))

    def get_sound(self, index):
        npk = self._npk

        info = npk.info(index)
        key = (index, info['name'])

        sound_temp = self._sound_temp
        sound = sound_temp.get(key)
        if sound is not None:
            return sound
        else:
            data = npk.load_file(index)

            sound = Bass(data)

            sound_temp[key] = sound
            return sound

    def get_current_info(self):
        npk = self._npk
        tw = self.tw_files
        index = tw.currentRow()
        info = npk.info(index)
        return index, info

    def play_current_sound(self, loop):
        index, info = self.get_current_info()
        if info is not None:
            sound = self.get_sound(index)
            sound.set_loop(loop)
            sound.play()

    def pause_current_sound(self):
        index, info = self.get_current_info()
        if info is not None:
            sound = self.get_sound(index)
            sound.pause()

    def stop_current_sound(self):
        index, info = self.get_current_info()
        if info is not None:
            sound = self.get_sound(index)
            sound.stop()

    def extract_current_file(self):
        ue = self._upper_event
        npk = self._npk
        index, info = self.get_current_info()

        extract_dir = ue['get_extract_dir']()
        if extract_dir is not None:
            [dirname, filename] = os.path.split(info['name'])

            data = npk.load_file(index)
            with open('%s/%s' % (extract_dir, filename), 'bw') as io:
                io.write(data)
