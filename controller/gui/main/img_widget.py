import json
import os
import traceback
from io import BytesIO

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QFileDialog, QTableWidgetItem
from pydnfex.hard_code import IMAGE_FORMAT_8888
from pydnfex.img import IMGFactory, ImageLink, Sprite
from pydnfex.img.image import SpriteZlibImage, Image
from pydnfex.img.version import IMGv5, IMGv6, IMGv4

from res.text import IMAGE_FORMAT_TEXT, IMAGE_EXTRA_TEXT
from util import common
from util.io_helper import IOHelper
from view.main.img_widget import Ui_IMGWidget
from ..progress_widget import ProgressWidget


class IMGWidget(Ui_IMGWidget, QWidget):
    def __init__(self, path, upper_event, img_name='', **kwargs):
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
        self._img = IMGFactory.open(io)
        self._pixmap_temp = {}
        self._changing = False
        self._name = img_name

        self.tw_images.currentItemChanged.connect(self._tw_images_current_item_changed)
        self.tw_images.cellChanged.connect(self._tw_images_cell_changed)
        self.tw_sprites.currentItemChanged.connect(self._tw_sprites_current_item_changed)
        self.tw_color_boards.currentItemChanged.connect(self._tw_color_boards_current_item_changed)

        self.refresh_images()
        self.refresh_sprites()
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
                image = img.images[index]
                if col == 2:
                    index = int(item.text())
                    image.set_image(img.images[index])
                elif col == 4:
                    [x, y] = list(map(item.text().split(',')))
                    image.x, image.y = x, y
                elif col == 6:
                    [mw, mh] = list(map(item.text().split(',')))
                    image.mw, image.mh = mw, mh
                elif col == 8:
                    image.sprite_index = int(item.text())
                elif col == 9:
                    [l, t, r, b] = list(map(int, item.text().split(',')))
                    image.left, image.top, image.right, image.bottom = l, t, r, b
            except Exception as e:
                traceback.print_exc()

    def refresh_color_boards(self):
        tw = self.tw_color_boards
        img = self._img

        row_count = tw.rowCount()
        color_boards = getattr(img, 'color_boards', [])
        color_board_count = len(color_boards)

        if row_count > color_board_count:
            for i in range(row_count - 1, color_board_count - 1, -1):
                tw.removeRow(i)
        else:
            for i in range(color_board_count - row_count):
                tw.insertRow(0)

        for i, color_board in enumerate(color_boards):
            tw.setItem(i, 0, common.qtwi_str(i))
            tw.setItem(i, 1, common.qtwi_str(len(color_board.colors)))

        tw.setCurrentCell(0, 0)

    def _tw_color_boards_current_item_changed(self, new, old):
        img = self._img

        index = self.tw_images.currentRow()
        image = img.image_by_index(index)

        if image is None:
            return

        pixmap = self.get_pixmap('normal', index, new.row())
        self.update_view(image.x, image.y, image.w, image.h, image.mw, image.mh, pixmap)

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

        for index, image in enumerate(img.images):
            target = image
            if isinstance(image, ImageLink):
                target = image.final_image
                tw.setItem(index, 2, common.qtwi_str(image.index))
            else:
                tw.setItem(index, 2, common.qtwi_str())

            tw.setItem(index, 0, common.qtwi_str(index))
            tw.setItem(index, 1, common.qtwi_str(IMAGE_FORMAT_TEXT.get(target.format, 'unknown')))
            tw.setItem(index, 3, common.qtwi_str(IMAGE_EXTRA_TEXT.get(target.extra, 'unknown')))
            tw.setItem(index, 4, common.qtwi_str('%s,%s' % (target.x, target.y)))
            tw.setItem(index, 5, common.qtwi_str('%s,%s' % (target.w, target.h)))
            tw.setItem(index, 6, common.qtwi_str('%s,%s' % (target.mw, target.mh)))
            tw.setItem(index, 7, common.qtwi_str(target.size))
            if isinstance(target, SpriteZlibImage):
                tw.setItem(index, 8, common.qtwi_str(target.sprite_index))
                tw.setItem(index, 9, common.qtwi_str('%s,%s,%s,%s' % (
                    target.left, target.top, target.right, target.bottom
                )))
            else:
                tw.setItem(index, 8, common.qtwi_str())
                tw.setItem(index, 9, common.qtwi_str())
        self._changing = False

    def refresh_sprites(self):
        tw = self.tw_sprites
        img = self._img

        row_count = tw.rowCount()
        sprites = getattr(img, 'sprites', [])
        sprite_count = len(sprites)

        if row_count > sprite_count:
            for i in range(row_count - 1, sprite_count - 1, -1):
                tw.removeRow(i)
        else:
            for i in range(sprite_count - row_count):
                tw.insertRow(0)

        for i, sprite in enumerate(sprites):
            tw.setItem(i, 0, common.qtwi_str(sprite.index))
            tw.setItem(i, 1, common.qtwi_str(sprite.data_size))
            tw.setItem(i, 2, common.qtwi_str(sprite.raw_size))
            tw.setItem(i, 3, common.qtwi_str('%s,%s' % (sprite.w, sprite.h)))

    def refresh_info(self):
        tw = self.tw_info
        img = self._img

        tw.setItem(0, 0, common.qtwi_str(img.version))
        tw.setItem(1, 0, common.qtwi_str(len(img.images)))
        tw.setItem(2, 0, common.qtwi_str(len(img.color_board.colors) if isinstance(img, IMGv4) else '-'))
        tw.setItem(3, 0, common.qtwi_str(len(img.sprites) if isinstance(img, IMGv5) else '-'))
        tw.setItem(4, 0, common.qtwi_str(len(img.color_boards) if isinstance(img, IMGv6) else '-'))

    def get_pixmap(self, img_type, index, color_board_index=None):
        img = self._img
        pixmap_temp = self._pixmap_temp

        key = (img_type, index, color_board_index)
        pixmap = pixmap_temp.get(key)
        if pixmap is not None:
            return pixmap
        else:
            if img_type == 'normal':
                image = img.image_by_index(index)
                if not image:
                    return None
                elif isinstance(img, ImageLink):
                    return self.get_pixmap(img_type, img.index, color_board_index)

                color_board = None
                if isinstance(img, IMGv6):
                    color_board = img.color_board_by_index(color_board_index)

                with BytesIO() as io:
                    img.build(image, color_board=color_board).save(io, format='png')
                    data = IOHelper.read_range(io)
            elif img_type == 'map':
                with BytesIO() as io:
                    img.sprite_by_index(index).build().save(io, format='png')
                    data = IOHelper.read_range(io)
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
            image = img.image_by_index(index)
            if isinstance(image, ImageLink):
                image = image.final_image

            color_board_index = self.tw_color_boards.currentRow()
            pixmap = self.get_pixmap('normal', index, color_board_index)
            self.update_view(image.x, image.y, image.w, image.h, image.mw, image.mh, pixmap)

    def _tw_sprites_current_item_changed(self, new, old):
        if new is not None:
            img = self._img

            index = new.row()
            sprite = img.sprite_by_index(index)

            pixmap = self.get_pixmap('map', index)
            self.update_view(0, 0, sprite.w, sprite.h, sprite.w, sprite.h, pixmap)

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
                color_board = None
                if color_board_index:
                    color_board = img.color_board_by_index(color_board_index)
                image = img.image_by_index(index)
                with BytesIO() as io:
                    img.build(image, color_board=color_board).save(io, format='png')
                    data = IOHelper.read_range(io)
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
                        color_board = None
                        if color_board_index:
                            color_board = img.color_board_by_index(color_board_index)
                        image = img.image_by_index(index)
                        with BytesIO() as io:
                            img.build(image, color_board=color_board).save(io, format='png')
                            data = IOHelper.read_range(io)
                        common.write_file(path, data)
                    else:
                        return False
            else:
                path = self.extract_gen_path(index, 'image')
                if path is not None:
                    image = img.image_by_index(index)
                    with BytesIO() as io:
                        img.build(image).save(io, format='png')
                        data = IOHelper.read_range(io)
                    common.write_file(path, data)
                else:
                    return False

        pw.close()

        return True

    def extract_current_sprite(self):
        img = self._img
        index = self.tw_sprites.currentRow()

        if index >= 0:
            path = self.extract_gen_path(index, 'sprite')
            if path is not None:
                data = img.sprite_by_index(index).build()
                common.write_file(path, data)

    def extract_all_sprite(self):
        img = self._img

        for index, sprite in enumerate(img.sprites):
            path = self.extract_gen_path(index, 'sprite')

            if path is not None:
                data = sprite.build()
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
                image = img.image_by_index(index)
                if isinstance(image, ImageLink):
                    image = image.final_image
                info.append({'x': image.x, 'y': image.y})

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
            image = Image(IMAGE_FORMAT_8888)
            image.set_data(data)
            img.images.insert(index, image)
        self.refresh_images()
        self.refresh_info()

    def replace_image(self):
        img = self._img
        index = self.tw_images.currentRow()

        [path, type] = QFileDialog.getOpenFileName(parent=self, caption='替换图像', directory='./',
                                                   filter='PNG 文件(*.png);;所有文件(*)')
        if os.path.exists(path):
            data = common.read_file(path)
            img.image_by_index(index).set_data(data)
        self.refresh_images()

    def remove_image(self):
        img = self._img
        index = self.tw_images.currentRow()

        img.remove_image(index)
        self.refresh_images()
        self.refresh_info()

    def insert_sprite(self):
        img = self._img
        index = self.tw_images.currentRow()

        [path, type] = QFileDialog.getOpenFileName(parent=self, caption='插入图像（sprite）', directory='./',
                                                   filter='PNG 文件(*.png);;所有文件(*)')
        if os.path.exists(path):
            data = common.read_file(path)
            sprite = Sprite(IMAGE_FORMAT_8888)
            sprite.set_data(data)
            img.insert_sprite(index, sprite)
        self.refresh_images()
        self.refresh_info()

    def replace_sprite(self):
        img = self._img
        index = self.tw_images.currentRow()

        [path, type] = QFileDialog.getOpenFileName(parent=self, caption='替换图像（sprite）', directory='./',
                                                   filter='PNG 文件(*.png);;所有文件(*)')
        if os.path.exists(path):
            data = common.read_file(path)
            img.sprite_by_index(index).set_data(data)
        self.refresh_images()

    def remove_sprite(self):
        img = self._img
        index = self.tw_images.currentRow()

        img.sprites.pop(index)
        self.remove_sprite()
        self.refresh_info()

    def save_img(self):
        [path, type] = QFileDialog.getSaveFileName(parent=self, caption='保存IMG文件', directory='./',
                                                   filter='IMG 文件(*.img);;所有文件(*)')
        img = self._img
        img.load_all()
        with open(path, 'bw') as io:
            img.save(io)
