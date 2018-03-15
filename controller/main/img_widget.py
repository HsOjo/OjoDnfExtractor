from io import BytesIO

from PyQt5.QtWidgets import QWidget, QTableWidgetItem

from model.img import IMG, IMAGE_FORMAT_LINK, IMAGE_EXTRA_DDS_ZLIB
from view.main.img_widget import Ui_IMGWidget


class IMGWidget(Ui_IMGWidget, QWidget):
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

        self._img = IMG(io)
        self.refresh_images()

    def refresh_images(self):
        tw = self.tw_images
        img = self._img

        row_count = tw.rowCount()
        file_count = len(img.images)

        if row_count > file_count:
            for i in range(row_count - 1, file_count - 1, -1):
                tw.removeRow(i)
        else:
            for i in range(file_count - row_count):
                tw.insertRow(0)

        for i, v in enumerate(img.images):
            info = img.info(v)
            qtwi_str = lambda x: QTableWidgetItem(str(x))

            tw.setItem(i, 0, qtwi_str(i))
            tw.setItem(i, 1, qtwi_str(info['format']))
            if info['format'] == IMAGE_FORMAT_LINK:
                tw.setItem(i, 2, qtwi_str(info['link']))
            else:
                tw.setItem(i, 3, qtwi_str(info['extra']))
                tw.setItem(i, 4, qtwi_str(info['w']))
                tw.setItem(i, 5, qtwi_str(info['h']))
                tw.setItem(i, 6, qtwi_str(info['size']))
                tw.setItem(i, 7, qtwi_str(info['x']))
                tw.setItem(i, 8, qtwi_str(info['y']))
                tw.setItem(i, 9, qtwi_str(info['mw']))
                tw.setItem(i, 10, qtwi_str(info['mh']))
                if info['extra'] == IMAGE_EXTRA_DDS_ZLIB:
                    tw.setItem(i, 11, qtwi_str(info['dds_index']))
                    tw.setItem(i, 12, qtwi_str(info['left']))
                    tw.setItem(i, 13, qtwi_str(info['top']))
                    tw.setItem(i, 14, qtwi_str(info['right']))
                    tw.setItem(i, 15, qtwi_str(info['bottom']))

