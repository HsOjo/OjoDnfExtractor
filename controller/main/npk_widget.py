import os
from io import BytesIO

from PyQt5.QtWidgets import QWidget, QTableWidgetItem

from model.npk import NPK
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
        self.refresh_files()

        self.pb_load_img.clicked.connect(self._pb_load_img_clicked)

    def _pb_load_img_clicked(self):
        ue = self._upper_event
        npk = self._npk
        tw = self.tw_files
        row = tw.currentRow()
        path = tw.item(row, 1).text()
        data = npk.load_file(path)
        [dirname, filename] = os.path.split(path)

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

        for i, v in enumerate(npk.files):
            info = npk.info(v)
            tw.setItem(i, 0, QTableWidgetItem(str(info['size'])))
            tw.setItem(i, 1, QTableWidgetItem(v))
