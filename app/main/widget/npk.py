import os
import traceback
from io import BytesIO, StringIO

from PyQt6.QtWidgets import QWidget, QFileDialog, QTableWidgetItem, QMessageBox
from pydnfex.npk import NPK, File

from app.libs.bass import Bass
from app import common
from app.res.window.main.widget.npk import Ui_NPKWidget
from .img import IMGWidget
from app.main.widget.progress import ProgressWidget


class NPKWidget(Ui_NPKWidget, QWidget):
    def __init__(self, path, upper_event, **kwargs):
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
        self._npk = NPK.open(io)
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
                    npk.file_by_index(index).name = item.text()
            except Exception as e:
                traceback.print_exc()

    def load_current_img(self, **kwargs):
        ue = self._upper_event
        npk = self._npk
        index = self.tw_files.currentRow()
        file = npk.file_by_index(index)
        if file is not None:
            file.load(force=kwargs.get('force', False))
            [dirname, filename] = os.path.split(file.name)
            ue['open_file']('img', filename, file.data, img_name=file.name, **kwargs)

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

        for i, f in enumerate(npk.files):
            tw.setItem(i, 0, common.qtwi_str(i))
            tw.setItem(i, 1, common.qtwi_str(getattr(f, '_offset')))
            tw.setItem(i, 2, common.qtwi_str(f.size))
            tw.setItem(i, 3, common.qtwi_str('Y' if common.is_std_name(f.name) else ''))
            tw.setItem(i, 4, common.qtwi_str(f.name))
        self._changing = False

    def get_sound(self, index):
        npk = self._npk

        file = npk.file_by_index(index)
        key = (index, file.name)

        sound_temp = self._sound_temp
        sound = sound_temp.get(key)
        if sound is not None:
            return sound
        else:
            sound = Bass(file.data)
            sound_temp[key] = sound
            return sound

    def get_current_sound(self):
        index = self.tw_files.currentRow()
        file = self._npk.file_by_index(index)
        if file is not None:
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

    def extract_gen_path(self, file):
        ue = self._upper_event

        extract_dir = ue['get_extract_dir']()
        extract_mode = ue['get_extract_mode']()

        if extract_dir is not None:
            [dirname, filename] = os.path.split(file.name)

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

        file = npk.file_by_index(index)
        if file is not None:
            path = self.extract_gen_path(file)
            if path is not None:
                common.write_file(path, file.data)

    def extract_all_file(self):
        npk = self._npk

        for file in npk.files:
            path = self.extract_gen_path(file)
            if path is not None:
                common.write_file(path, file.data)
            else:
                break

    def extract_img_all(self):
        ue = self._upper_event
        npk = self._npk

        pw = ProgressWidget()
        pw.set_max(len(npk.files) - 1)
        pw.set_title('提取所有IMG内容中...')
        pw.show()
        for index, file in enumerate(npk.files):
            pw.set_value(index)
            ue['process_events']()
            if pw.cancel:
                return False

            imgw = IMGWidget(file.data, self._upper_event, file.name)
            try:
                if not imgw.extract_pos_info():
                    break
                if not imgw.extract_all_sprite():
                    break
                if not imgw.extract_all_image():
                    break
            except:
                with StringIO() as io:
                    traceback.print_exc(file=io)
                    io.seek(0)
                    content = io.read()
                QMessageBox.warning(None, '错误：', '''%s\n\n%s''' % (file.name, content))

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
            npk.files.insert(index, File(filename, data))
        self.refresh_files()

    def replace_file(self):
        npk = self._npk
        index = self.tw_files.currentRow()

        [path, type] = QFileDialog.getOpenFileName(parent=self, caption='替换文件', directory='./',
                                                   filter='IMG 文件(*.img);;OGG 文件(*.ogg);;所有文件(*)')
        if os.path.exists(path):
            data = common.read_file(path)
            npk.file_by_index(index).set_data(data)
        self.refresh_files()

    def remove_file(self):
        npk = self._npk
        index = self.tw_files.currentRow()

        npk.files.pop(index)
        self.refresh_files()

    def clean_no_std(self):
        npk = self._npk
        for index, file in enumerate(reversed(npk.files)):
            if not common.is_std_name(file.name):
                npk.files.pop(index)
        self.refresh_files()

    def clean_duplicate(self):
        npk = self._npk

        dup_list = []
        for index, file in enumerate(reversed(npk.files)):
            item = (getattr(file, '_offset'), file.size)
            if item in dup_list:
                npk.files.pop(index)
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
