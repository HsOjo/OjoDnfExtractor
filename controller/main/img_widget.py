import os
from io import BytesIO

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget

from model.img import IMG, IMAGE_FORMAT_LINK, IMAGE_EXTRA_MAP_ZLIB, IMAGE_FORMAT_TEXT, IMAGE_EXTRA_TEXT
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
        self._pixmap_temp = {}

        self.tw_images.currentItemChanged.connect(self._tw_images_current_item_changed)
        self.tw_map_images.currentItemChanged.connect(self._tw_map_images_current_item_changed)

        self.refresh_images()
        self.refresh_map_images()
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
                if info['extra'] == IMAGE_EXTRA_MAP_ZLIB:
                    tw.setItem(i, 8, common.qtwi_str(info['map_index']))
                    tw.setItem(i, 9,
                               common.qtwi_str(
                                   '%s,%s,%s,%s' % (info['left'], info['top'], info['right'], info['bottom'])))

    def refresh_map_images(self):
        tw = self.tw_map_images
        img = self._img

        row_count = tw.rowCount()
        image_count = len(img.map_images)

        if row_count > image_count:
            for i in range(row_count - 1, image_count - 1, -1):
                tw.removeRow(i)
        else:
            for i in range(image_count - row_count):
                tw.insertRow(0)

        for i, v in enumerate(img.map_images):
            info = img.info_map(v)

            tw.setItem(i, 0, common.qtwi_str(info['index']))
            tw.setItem(i, 1, common.qtwi_str(info['data_size']))
            tw.setItem(i, 2, common.qtwi_str(info['raw_size']))
            tw.setItem(i, 3, common.qtwi_str('%s,%s' % (info['w'], info['h'])))

    def refresh_info(self):
        tw = self.tw_info
        img = self._img

        tw.setItem(0, 0, common.qtwi_str('v%s' % img.version))
        tw.setItem(1, 0, common.qtwi_str(len(img.images)))
        tw.setItem(2, 0, common.qtwi_str(len(img.color_board)))
        tw.setItem(3, 0, common.qtwi_str(len(img.map_images)))
        tw.setItem(4, 0, common.qtwi_str(len(img.color_boards)))

    def get_pixmap(self, img_type, index, color_board_index=None):
        img = self._img
        pixmap_temp = self._pixmap_temp

        key = (img_type, index, color_board_index)
        pixmap = pixmap_temp.get(key)
        if pixmap is not None:
            return pixmap
        else:
            if img_type == 'normal':
                data = img.build(index, color_board_index)
            elif img_type == 'map':
                data = img.build_map(index)
            else:
                raise Exception('Unknown img_type.')

            pixmap = QPixmap()
            pixmap.loadFromData(data)

            pixmap_temp[key] = pixmap
            return pixmap

    def _tw_images_current_item_changed(self, new, old):
        if new is not None:
            ue = self._upper_event
            img = self._img

            index = new.row()
            color_board_index = self.tw_color_boards.currentRow()
            pixmap = self.get_pixmap('normal', index, color_board_index)

            info = img.info(index)
            ue['set_canvas'](info['mw'], info['mh'])
            ue['set_texture'](info['x'], info['y'], info['w'], info['h'], pixmap)

    def _tw_map_images_current_item_changed(self, new, old):
        if new is not None:
            ue = self._upper_event
            img = self._img

            index = new.row()
            pixmap = self.get_pixmap('map', index)

            info = img.info_map(index)
            ue['set_canvas'](info['w'], info['h'])
            ue['set_texture'](0, 0, info['w'], info['h'], pixmap)

    def extract_gen_path(self, index, data_type):
        ue = self._upper_event

        extract_dir = ue['get_extract_dir']()
        extract_mode = ue['get_extract_mode']()

        if extract_dir is not None:
            if extract_mode == 'raw':
                path = '%s/%s.png' % (extract_dir, index)
            elif extract_mode == 'wodir':
                dirname = '%s/%s' % (extract_dir, data_type)
                os.makedirs(dirname, exist_ok=True)
                path = '%s/%s.png' % (dirname, index)
            else:
                raise Exception('Unsupport mode: %s' % extract_mode)

            return path

    def extract_current_image(self):
        img = self._img
        index = self.tw_images.currentRow()
        color_board_index = self.tw_color_boards.currentRow()

        if index >= 0:
            if color_board_index < 0:
                path = self.extract_gen_path(index, 'image')
            else:
                path = self.extract_gen_path(index, 'image_color_%s' % color_board_index)

            if path is not None:
                data = img.build(index, color_board_index)
                common.write_file(path, data)

    def extract_all_image(self):
        img = self._img
        color_board_index = self.tw_color_boards.currentRow()

        for index in img.images:
            if color_board_index < 0:
                path = self.extract_gen_path(index, 'image')
            else:
                path = self.extract_gen_path(index, 'image_color_%s' % color_board_index)

            if path is not None:
                data = img.build(index, color_board_index)
                common.write_file(path, data)
            else:
                break

    def extract_current_map_image(self):
        img = self._img
        index = self.tw_map_images.currentRow()

        if index >= 0:
            path = self.extract_gen_path(index, 'map_image')
            if path is not None:
                data = img.build_map(index)
                common.write_file(path, data)

    def extract_all_map_image(self):
        img = self._img

        for index in img.map_images:
            path = self.extract_gen_path(index, 'map_image')

            if path is not None:
                data = img.build_map(index)
                common.write_file(path, data)
            else:
                break
