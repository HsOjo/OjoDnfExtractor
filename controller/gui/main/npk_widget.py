import os
import traceback
from io import BytesIO, StringIO

from PyQt5.QtWidgets import QWidget, QFileDialog, QTableWidgetItem, QMessageBox

from lib.bass import Bass
from model.npk import NPK
from util import common
from view.main.npk_widget import Ui_NPKWidget
from .img_widget import IMGWidget
from ..progress_widget import ProgressWidget


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

        self._io = io
        self._npk = NPK(io)
        self._sound = None
        self._sound_temp = {}
        self._changing = False

        self.tw_files.cellChanged.connect(self._tw_files_cell_changed)

        self.refresh_files()

    def __del__(self):
        self._io.close()

    def _tw_files_cell_changed(self, row, col):
        if not self._changing:
            tw = self.tw_files
            npk = self._npk
            index = row
            item = tw.item(row, col)  # type: QTableWidgetItem
            try:
                if col == 2:
                    npk.set_info(index, 'name', item.text())
            except Exception as e:
                traceback.print_exc()

    def load_current_img(self):
        ue = self._upper_event
        npk = self._npk
        index = self.tw_files.currentRow()
        info = npk.info(index)
        if info is not None:
            data = npk.load_file(index)
            [dirname, filename] = os.path.split(info['name'])

            ue['open_file']('img', filename, data, img_name=info['name'])

    def refresh_files(self):
        self._changing = True
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
            tw.setItem(i, 1, common.qtwi_str(info['offset']))
            tw.setItem(i, 2, common.qtwi_str(info['size']))
            tw.setItem(i, 3, common.qtwi_str('Y' if common.is_std_name(info['name']) else ''))
            tw.setItem(i, 4, common.qtwi_str(info['name']))
        self._changing = False

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

    def get_current_sound(self):
        index = self.tw_files.currentRow()
        info = self._npk.info(index)
        if info is not None:
            sound = self.get_sound(index)  # type: Bass
            return sound

    def play_current_sound(self, loop):
        sound = self.get_current_sound()
        if sound is not None:
            sound.set_loop(loop)
            sound.play()

    def pause_current_sound(self):
        sound = self.get_current_sound()
        if sound is not None:
            sound.pause()

    def stop_current_sound(self):
        sound = self.get_current_sound()
        if sound is not None:
            sound.stop()

    def extract_gen_path(self, index):
        ue = self._upper_event
        npk = self._npk

        extract_dir = ue['get_extract_dir']()
        extract_mode = ue['get_extract_mode']()

        if extract_dir is not None:
            info = npk.info(index)
            [dirname, filename] = os.path.split(info['name'])

            if extract_mode == 'raw':
                dir_ = extract_dir + '/%s' % dirname
                os.makedirs(dir_, exist_ok=True)
                path = '%s/%s' % (dir_, filename)
            elif extract_mode == 'wodir':
                path = '%s/%s' % (extract_dir, filename)
            else:
                raise Exception('Unsupport mode: %s' % extract_mode)

            return path

    def extract_current_file(self):
        npk = self._npk

        index = self.tw_files.currentRow()

        if index >= 0:
            path = self.extract_gen_path(index)

            if path is not None:
                data = npk.load_file(index)
                common.write_file(path, data)

    def extract_all_file(self):
        npk = self._npk

        for index in npk.files:
            path = self.extract_gen_path(index)
            if path is not None:
                data = npk.load_file(index)
                common.write_file(path, data)
            else:
                break

    def extract_img_all(self):
        ue = self._upper_event
        npk = self._npk

        pw = ProgressWidget()
        pw.set_max(len(npk.files) - 1)
        pw.set_title('提取所有IMG内容中...')
        pw.show()
        for index in npk.files:
            pw.set_value(index)
            ue['process_events']()
            if pw.cancel:
                return False

            info = npk.info(index)
            imgw = IMGWidget(npk.load_file(index), self._upper_event, info['name'])
            try:
                if not imgw.extract_pos_info():
                    break
                if not imgw.extract_all_map_image():
                    break
                if not imgw.extract_all_image():
                    break
            except:
                with StringIO() as io:
                    traceback.print_exc(file=io)
                    io.seek(0)
                    content = io.read()
                QMessageBox.warning(None, '错误：', '''%s\n\n%s''' % (info['name'], content))

        pw.close()

        return True

    def insert_file(self):
        npk = self._npk
        index = self.tw_files.currentRow()

        [path, type] = QFileDialog.getOpenFileName(parent=self, caption='插入文件', directory='./',
                                                   filter='IMG 文件(*.img);;OGG 文件(*.ogg);;所有文件(*)')
        if os.path.exists(path):
            [dirname, filename] = os.path.split(path)
            data = common.read_file(path)
            npk.insert_file(index, filename, data)
        self.refresh_files()

    def replace_file(self):
        npk = self._npk
        index = self.tw_files.currentRow()

        [path, type] = QFileDialog.getOpenFileName(parent=self, caption='替换文件', directory='./',
                                                   filter='IMG 文件(*.img);;OGG 文件(*.ogg);;所有文件(*)')
        if os.path.exists(path):
            [dirname, filename] = os.path.split(path)
            data = common.read_file(path)
            npk.replace_file(index, data)
        self.refresh_files()

    def remove_file(self):
        npk = self._npk
        index = self.tw_files.currentRow()

        npk.remove_file(index)
        self.refresh_files()

    def clean_no_std(self):
        npk = self._npk
        for index in reversed(npk.files):
            if not common.is_std_name(npk.info(index).get('name', '')):
                npk.remove_file(index)
        self.refresh_files()

    def clean_duplicate(self):
        npk = self._npk

        dup_list = []
        for index in reversed(npk.files):
            info = npk.info(index)
            item = (info['offset'], info['size'])
            if item in dup_list:
                npk.remove_file(index)
            else:
                dup_list.append(item)
        self.refresh_files()

    def save_npk(self):
        [path, type] = QFileDialog.getSaveFileName(parent=self, caption='保存NPK文件', directory='./',
                                                   filter='NPK 文件(*.npk);;所有文件(*)')
        npk = self._npk
        npk.load_all()
        with open(path, 'bw') as io:
            npk.save(io)
