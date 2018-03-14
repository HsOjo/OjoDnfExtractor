from io import BytesIO

from PyQt5.QtWidgets import QWidget, QTableWidgetItem

from model.npk import NPK
from view.main.npk_widget import Ui_NPKWidget


class NPKWidget(Ui_NPKWidget, QWidget):
    def __init__(self, path):
        super().__init__()
        self.setupUi(self)

        if type(path) == bytes:
            io = BytesIO(path)
        elif type(path) == str:
            io = open(path, 'br+')
        else:
            raise Exception('Unsupport value type.')

        self._npk = NPK(io)
        self.refresh_files()

    def refresh_files(self):
        tw = self.tw_file_list
        npk = self._npk

        row_count = tw.rowCount()
        file_count = len(npk.files)

        if row_count > file_count:
            for i in range(row_count - 1, file_count - 1, -1):
                tw.removeRow(i)
        else:
            for i in range(file_count - row_count):
                tw.insertRow(0)

        for i, v in enumerate(npk.files):
            info = npk.info(v)
            tw.setItem(i, 0, QTableWidgetItem(str(info['size'])))
            tw.setItem(i, 1, QTableWidgetItem(v))
