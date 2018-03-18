import os

from model.img import IMG, IMAGE_EXTRA_TEXT, IMAGE_FORMAT_TEXT
from util import common
from util.terminal import Terminal


class IMGTerminal(Terminal):
    def __init__(self, img: IMG):
        super().__init__('OjoEx[IMG]> ')
        self._img = img

        self.bind_function('version', lambda: print(img.version), {}, 'print IMG version.')
        self.bind_function('images', lambda: print(img.images), {}, 'print image list.')
        self.bind_function('map_images', lambda: print(img.map_images), {}, 'print map image list.')
        self.bind_function('info', self.info, {
            'index': {'type': int, 'null': True, 'help': 'image index in image list'},
        }, 'print image info.')
        self.bind_function('info_map', self.info_map, {
            'index': {'type': int, 'null': True, 'help': 'map_image index in map_image list'},
        }, 'print map_image info.')
        self.bind_function('color_board', lambda: print(img.color_board), {}, 'print color board.')
        self.bind_function('color_boards', lambda: print(img.color_boards), {}, 'print color boards.')
        self.bind_function('load_all', img.load_all, {}, 'load all images.')
        self.bind_function('extract', lambda file, index, color_board_index=0: common.write_file(file, img.build(index,
                                                                                                                 color_board_index)),
                           {
                               'file': {'type': str, 'help': 'save file path.'},
                               'index': {'type': int, 'help': 'image index in image list'},
                               'color_board_index': {'type': int, 'null': True,
                                                     'help': 'color_board_index in color_board list'},
                           }, 'extract png image.')
        self.bind_function('extract_all', self.extract_all, {
            'dir': {'type': str, 'help': 'path of extract dir.'},
            'color_board_index': {'type': int, 'null': True,
                                  'help': 'color_board_index in color_board list'},
        }, 'extract all images to directory.')
        self.bind_function('extract_map', lambda file, index: common.write_file(file, img.build_map(index)),
                           {
                               'file': {'type': str, 'help': 'save file path.'},
                               'index': {'type': int, 'help': 'image index in image list'},
                           }, 'extract map png image.')
        self.bind_function('extract_map_all', self.extract_map_all, {
            'dir': {'type': str, 'help': 'path of extract dir.'},
        }, 'extract all map images to directory.')

    def extract_all(self, path_dir, color_board_index=0):
        img = self._img
        img.load_all()
        os.makedirs(path_dir, exist_ok=True)
        for i in img.images:
            print('writing: %s' % i)
            data = img.build(i, color_board_index)
            path = '%s/%s.png' % (path_dir, i)
            common.write_file(path, data)

    def extract_map_all(self, path_dir):
        img = self._img
        img.load_all()
        os.makedirs(path_dir, exist_ok=True)
        for i in img.map_images:
            print('writing: %s' % i)
            data = img.build_map(i)
            path = '%s/%s.png' % (path_dir, i)
            common.write_file(path, data)

    def info(self, index=None):
        img = self._img
        if index is not None:
            print(img.info(index))
        else:
            for i in img.images:
                info = img.info(i)
                info['extra'] = IMAGE_EXTRA_TEXT.get(info['extra'], 'unknown')
                info['format'] = IMAGE_FORMAT_TEXT.get(info['format'], 'unknown')
                print(i, info)

    def info_map(self, index=None):
        img = self._img
        if index is not None:
            print(img.info_map(index))
        else:
            for i in img.map_images:
                info = img.info_map(i)
                info['format'] = IMAGE_FORMAT_TEXT.get(info['format'], 'unknown')
                print(i, info)
