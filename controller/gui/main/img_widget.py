import json
import os
import traceback
from io import BytesIO

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QFileDialog, QTableWidgetItem

from model.img import IMG, IMAGE_FORMAT_LINK, IMAGE_EXTRA_MAP_ZLIB, IMAGE_FORMAT_TEXT, IMAGE_EXTRA_TEXT
from util import common
from view.main.img_widget import Ui_IMGWidget
from ..progress_widget import ProgressWidget


class IMGWidget(Ui_IMGWidget, QWidget):
    def __init__(self, path, upper_event, name):
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
        self._img = IMG(io)
        self._pixmap_temp = {}
        self._changing = False
        self._name = name

        self.tw_images.currentItemChanged.connect(self._tw_images_current_item_changed)
        self.tw_images.cellChanged.connect(self._tw_images_cell_changed)
        self.tw_map_images.currentItemChanged.connect(self._tw_map_images_current_item_changed)
        self.tw_color_boards.currentItemChanged.connect(self._tw_color_boards_current_item_changed)

        self.refresh_images()
        self.refresh_map_images()
        self.refresh_info()
        self.refresh_color_boards()

    def __del__(self):
        self._io.close()

    def _tw_images_cell_changed(self, row, col):
        if not self._changing:
            tw = self.tw_images
            img = self._img
            index = row
            item = tw.item(row, col)  # type: QTableWidgetItem
            try:
                if col == 2:
                    img.set_info(index, 'link', int(item.text()))
                elif col == 4:
                    [x, y] = item.text().split(',')
                    img.set_info(index, 'x', int(x))
                    img.set_info(index, 'y', int(y))
                elif col == 6:
                    [mw, mh] = item.text().split(',')
                    img.set_info(index, 'mw', int(mw))
                    img.set_info(index, 'mh', int(mh))
                elif col == 8:
                    img.set_info(index, 'map_index', int(item.text()))
                elif col == 9:
                    [l, t, r, b] = item.text().split(',')
                    img.set_info(index, 'left', int(l))
                    img.set_info(index, 'top', int(t))
                    img.set_info(index, 'right', int(r))
                    img.set_info(index, 'bottom', int(b))
            except Exception as e:
                traceback.print_exc()

    def refresh_color_boards(self):
        tw = self.tw_color_boards
        img = self._img

        row_count = tw.rowCount()
        color_board_count = len(img.color_boards)

        if row_count > color_board_count:
            for i in range(row_count - 1, color_board_count - 1, -1):
                tw.removeRow(i)
        else:
            for i in range(color_board_count - row_count):
                tw.insertRow(0)

        for i, v in enumerate(img.color_boards):
            tw.setItem(i, 0, common.qtwi_str(i))
            tw.setItem(i, 1, common.qtwi_str(len(v)))

        tw.setCurrentCell(0, 0)

    def _tw_color_boards_current_item_changed(self, new, old):
        img = self._img

        index = self.tw_images.currentRow()
        info = img.info(index)

        pixmap = self.get_pixmap('normal', index, new.row())
        self.update_view(info['x'], info['y'], info['w'], info['h'], info['mw'], info['mh'], pixmap)

    def refresh_images(self):
        self._changing = True
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
                tw.setItem(i, 2, common.qtwi_str())
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
            else:
                tw.setItem(i, 8, common.qtwi_str())
                tw.setItem(i, 9, common.qtwi_str())
        self._changing = False

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

    def update_view(self, x, y, w, h, cw, ch, pixmap):
        ue = self._upper_event
        ue['set_canvas'](cw, ch)
        ue['set_texture'](x, y, w, h, pixmap)

    def _tw_images_current_item_changed(self, new, old):
        if new is not None:
            img = self._img

            index = new.row()
            info = img.info(index)
            if info['format'] == IMAGE_FORMAT_LINK:
                index = info['link']
                info = img.info(info['link'])

            color_board_index = self.tw_color_boards.currentRow()
            pixmap = self.get_pixmap('normal', index, color_board_index)
            self.update_view(info['x'], info['y'], info['w'], info['h'], info['mw'], info['mh'], pixmap)

    def _tw_map_images_current_item_changed(self, new, old):
        if new is not None:
            img = self._img

            index = new.row()
            info = img.info_map(index)

            pixmap = self.get_pixmap('map', index)
            self.update_view(0, 0, info['w'], info['h'], info['w'], info['h'], pixmap)

    def extract_gen_dir(self):
        ue = self._upper_event
        name = common.get_filename_wo_ext(self._name)

        extract_dir = ue['get_extract_dir']()
        extract_mode = ue['get_extract_mode']()

        if extract_dir is not None:
            if extract_mode == 'raw':
                ex_dir = '%s/%s' % (extract_dir, name)
            elif extract_mode == 'wodir':
                dirname, filename = os.path.split(name)
                ex_dir = '%s/%s/%s' % (extract_dir, dirname.replace('/', '_'), filename)
            else:
                raise Exception('Unsupport mode: %s' % extract_mode)

            os.makedirs(ex_dir, exist_ok=True)
            return ex_dir

    def extract_gen_path(self, index, data_type):
        ex_dir = self.extract_gen_dir()

        if ex_dir is not None:
            dirname = '%s/%s' % (ex_dir, data_type)
            os.makedirs(dirname, exist_ok=True)
            path = '%s/%s.png' % (dirname, index)

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
        ue = self._upper_event
        img = self._img
        count_color_boards = len(img.color_boards)

        pw = ProgressWidget()
        pw.set_max(len(img.images) - 1)
        pw.set_title('提取所有图片中...')
        pw.show()
        for index in img.images:
            pw.set_value(index)
            ue['process_events']()
            if pw.cancel:
                return False

            if count_color_boards > 0:
                for color_board_index in range(count_color_boards):
                    path = self.extract_gen_path(index, 'image_color_%s' % color_board_index)
                    if path is not None:
                        data = img.build(index, color_board_index)
                        common.write_file(path, data)
                    else:
                        return False
            else:
                path = self.extract_gen_path(index, 'image')
                if path is not None:
                    data = img.build(index, 0)
                    common.write_file(path, data)
                else:
                    return False

        pw.close()

        return True

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
                return False

        return True

    def extract_pos_info(self):
        img = self._img

        ex_dir = self.extract_gen_dir()
        if ex_dir is not None:
            path = '%s/%s' % (ex_dir, 'info.json')

            info = []
            for index in img.images:
                i = img.info(index)
                info.append({'x': i['x'], 'y': i['y']})

            with open(path, 'w') as io:
                json.dump(info, io, ensure_ascii=False)

            return True

        return False

    def insert_image(self):
        img = self._img
        index = self.tw_images.currentRow()

        [path, type] = QFileDialog.getOpenFileName(parent=self, caption='插入图像', directory='./',
                                                   filter='PNG 文件(*.png);;所有文件(*)')
        if os.path.exists(path):
            data = common.read_file(path)
            img.insert_image(index, data)
        self.refresh_images()
        self.refresh_info()

    def replace_image(self):
        img = self._img
        index = self.tw_images.currentRow()

        [path, type] = QFileDialog.getOpenFileName(parent=self, caption='替换图像', directory='./',
                                                   filter='PNG 文件(*.png);;所有文件(*)')
        if os.path.exists(path):
            data = common.read_file(path)
            img.replace_image(index, data)
        self.refresh_images()

    def remove_image(self):
        img = self._img
        index = self.tw_images.currentRow()

        img.remove_image(index)
        self.refresh_images()
        self.refresh_info()

    def insert_map_image(self):
        img = self._img
        index = self.tw_images.currentRow()

        [path, type] = QFileDialog.getOpenFileName(parent=self, caption='插入图像（map）', directory='./',
                                                   filter='PNG 文件(*.png);;所有文件(*)')
        if os.path.exists(path):
            data = common.read_file(path)
            img.insert_map_image(index, data)
        self.refresh_images()
        self.refresh_info()

    def replace_map_image(self):
        img = self._img
        index = self.tw_images.currentRow()

        [path, type] = QFileDialog.getOpenFileName(parent=self, caption='替换图像（map）', directory='./',
                                                   filter='PNG 文件(*.png);;所有文件(*)')
        if os.path.exists(path):
            data = common.read_file(path)
            img.replace_map_image(index, data)
        self.refresh_images()

    def remove_map_image(self):
        img = self._img
        index = self.tw_images.currentRow()

        img.remove_image(index)
        self.remove_map_image()
        self.refresh_info()

    def save_img(self):
        [path, type] = QFileDialog.getSaveFileName(parent=self, caption='保存IMG文件', directory='./',
                                                   filter='IMG 文件(*.img);;所有文件(*)')
        img = self._img
        img.load_all()
        with open(path, 'bw') as io:
            img.save(io)
