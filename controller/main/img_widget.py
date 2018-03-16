from io import BytesIO

from PyQt5.QtWidgets import QWidget

from model.img import IMG, IMAGE_FORMAT_LINK, IMAGE_EXTRA_DDS_ZLIB, IMAGE_FORMAT_TEXT, IMAGE_EXTRA_TEXT
from util import common
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
        self.refresh_dds_images()
        self.refresh_info()

    def refresh_images(self):
        tw = self.tw_images
        img = self._img

        row_count = tw.rowCount()
        image_count = len(img.images)

        if row_count > image_count:
            for i in range(row_count - 1, image_count - 1, -1):
                tw.removeRow(i)
        else:
            for i in range(image_count - row_count):
                tw.insertRow(0)

        for i, v in enumerate(img.images):
            info = img.info(v)

            tw.setItem(i, 0, common.qtwi_str(i))
            tw.setItem(i, 1, common.qtwi_str(IMAGE_FORMAT_TEXT.get(info['format'], 'unknown')))
            if info['format'] == IMAGE_FORMAT_LINK:
                tw.setItem(i, 2, common.qtwi_str(info['link']))
            else:
                tw.setItem(i, 3, common.qtwi_str(IMAGE_EXTRA_TEXT.get(info['extra'], 'unknown')))
                tw.setItem(i, 4, common.qtwi_str('%s,%s' % (info['x'], info['y'])))
                tw.setItem(i, 5, common.qtwi_str('%s,%s' % (info['w'], info['h'])))
                tw.setItem(i, 6, common.qtwi_str('%s,%s' % (info['mw'], info['mh'])))
                tw.setItem(i, 7, common.qtwi_str(info['size']))
                if info['extra'] == IMAGE_EXTRA_DDS_ZLIB:
                    tw.setItem(i, 8, common.qtwi_str(info['dds_index']))
                    tw.setItem(i, 9,
                               common.qtwi_str(
                                   '%s,%s,%s,%s' % (info['left'], info['top'], info['right'], info['bottom'])))

    def refresh_dds_images(self):
        tw = self.tw_dds_images
        img = self._img

        row_count = tw.rowCount()
        image_count = len(img.dds_images)

        if row_count > image_count:
            for i in range(row_count - 1, image_count - 1, -1):
                tw.removeRow(i)
        else:
            for i in range(image_count - row_count):
                tw.insertRow(0)

        for i, v in enumerate(img.dds_images):
            info = img.info_dds(v)

            tw.setItem(i, 0, common.qtwi_str(info['index']))
            tw.setItem(i, 1, common.qtwi_str(info['data_size']))
            tw.setItem(i, 2, common.qtwi_str(info['raw_size']))
            tw.setItem(i, 3, common.qtwi_str('%s,%s' % (info['w'], info['h'])))

    def refresh_info(self):
        tw = self.tw_info
        img = self._img

        tw.setItem(0, 0, common.qtwi_str(img.version))
        tw.setItem(1, 0, common.qtwi_str(len(img.images)))
        tw.setItem(2, 0, common.qtwi_str(len(img.dds_images)))
        tw.setItem(3, 0, common.qtwi_str(len(img.color_boards)))
