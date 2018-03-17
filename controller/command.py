import os
from io import BytesIO

from lib.bass import Bass
from model.img import IMG
from model.npk import NPK
from util import common
from util.terminal import Terminal


class NPKTerminal(Terminal):
    def __init__(self, npk: NPK):
        super().__init__('OjoEx[NPK]> ')
        self._npk = npk

        self.bind_function('files', lambda: print(npk.files), {}, 'print file list.')
        self.bind_function('info', self.info, {
            'index': {'type': int, 'null': True, 'help': 'file index in file list'},
        }, 'print file info.')
        self.bind_function('extract', lambda file, index: common.write_file(file, npk.load_file(index)), {
            'file': {'type': str, 'help': 'save file path.'},
            'index': {'type': int, 'help': 'file index in file list'},
        }, 'extract img file.')
        self.bind_function('open', self.open, {
            'type': {'type': str, 'help': 'open file type, img/ogg'},
            'file': {'type': str, 'help': 'file name in file list.'},
        }, 'open a file in file list.')
        self.bind_function('load_all', npk.load_file_all, {}, 'load all files.')
        self.bind_function('extract_all', self.extract_all, {
            'dir': {'type': str, 'help': 'path of extract dir.'},
            'mode': {'type': str, 'null': True, 'help': 'mode with filename. choices: wodir(default), raw'},
        }, 'extract all files to directory.')

    def extract_all(self, path_dir, mode='wodir'):
        npk = self._npk
        npk.load_file_all()
        os.makedirs(path_dir, exist_ok=True)
        for i in npk.files:
            info = npk.info(i)
            [dirname, filename] = os.path.split(info['name'])
            data = npk.load_file(i)
            print('writing: %s' % filename)
            os.makedirs(path_dir, exist_ok=True)
            if mode == 'raw':
                dir_ = path_dir + '/%s' % dirname
                os.makedirs(dir_, exist_ok=True)
                with open('%s/%s' % (dir_, filename), 'bw') as io:
                    io.write(data)
            elif mode == 'wodir':
                with open('%s/%s' % (path_dir, filename), 'bw') as io:
                    io.write(data)

    def open(self, type_, file):
        npk = self._npk
        if type_ == 'img':
            with BytesIO(npk.load_file(file)) as io:
                IMGTerminal(IMG(io)).start()
        elif type_ == 'ogg':
            ogg = Bass(npk.load_file(file))
            OGGTerminal(ogg).start()
            ogg.destroy()
        else:
            raise Exception('Unsupport type_: %s' % type_)

    def info(self, index=None):
        npk = self._npk
        if index is not None:
            print(npk.info(index))
        else:
            for i in npk.files:
                print(i, npk.info(i))


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
        self.bind_function('extract', lambda file, index, color_board_index=0: common.write_file(file, img.build(index,
                                                                                                                 color_board_index)),
                           {
                               'file': {'type': str, 'help': 'save file path.'},
                               'index': {'type': int, 'help': 'image index in image list'},
                               'color_board_index': {'type': int, 'null': True,
                                                     'help': 'color_board_index in color_board list'},
                           }, 'extract png file.')
        self.bind_function('load_all', img.load_all, {}, 'load all images.')
        self.bind_function('extract_all', self.extract_all, {
            'dir': {'type': str, 'help': 'path of extract dir.'},
            'color_board_index': {'type': int, 'null': True,
                                  'help': 'color_board_index in color_board list'},
        }, 'extract all images to directory.')

    def extract_all(self, path_dir, color_board_index=0):
        img = self._img
        img.load_all()
        os.makedirs(path_dir, exist_ok=True)
        for i in img.images:
            print('writing: %s' % i)
            data = img.build(i, color_board_index)
            with open('%s/%s.png' % (path_dir, i), 'bw') as io:
                io.write(data)

    def info(self, index=None):
        img = self._img
        if index is not None:
            print(img.info(index))
        else:
            for i in img.images:
                print(i, img.info(i))

    def info_map(self, index=None):
        img = self._img
        if index is not None:
            print(img.info_map(index))
        else:
            for i in img.map_images:
                print(i, img.info_map(i))


class OGGTerminal(Terminal):
    def __init__(self, ogg: Bass):
        self._ogg = ogg
        super().__init__('OjoEx[OGG]> ')
        ogg.get_lentime()
        self.bind_function('set_loop', ogg.set_loop, {
            '_loop': {'type': bool, 'help': 'is _loop.'}
        }, 'sound _loop play.')
        self.bind_function('play', ogg.play, {
            'replay': {'type': bool, 'null': True, 'help': 'is replay.'}
        }, 'play sound.')
        self.bind_function('pause', ogg.pause, {}, 'pause sound.')
        self.bind_function('stop', ogg.stop, {}, 'stop sound.')
        self.bind_function('get_volume', lambda: print(ogg.get_volume()), {}, 'get volume.')
        self.bind_function('set_volume', ogg.set_volume, {
            'volume': {'type': float, 'help': 'volume size.'}
        }, 'change sound volume.')
        self.bind_function('get_speed', lambda: print(ogg.get_speed()), {}, 'get speed.')
        self.bind_function('set_speed', ogg.set_speed, {
            'speed': {'type': float, 'help': 'speed value.'}
        }, 'change sound speed.')
        self.bind_function('get_playtime', lambda: print(ogg.get_playtime()), {}, 'get time of play progress.')
        self.bind_function('set_playtime', ogg.set_playtime, {
            'playtime': {'type': float, 'help': 'time of play progress.'}
        }, 'change sound play time.')
        self.bind_function('get_lentime', lambda: print(ogg.get_lentime()), {}, 'get time of sound length.')


class Command:
    def __init__(self, args):
        self.args = args
        self._term = Terminal('OjoDnfExtractor> ')
        self._term.bind_function('open', self.open, {
            'type': {'type': str, 'help': 'open file type, img/npk'},
            'file': {'type': str, 'help': 'open file path'},
        }, 'open a file.')

    def start(self):
        self._term.start()
        return 0

    def open(self, type, file):
        if type == 'npk':
            with open(file, 'rb+') as io:
                NPKTerminal(NPK(io)).start()
        elif type == 'img':
            with open(file, 'rb+') as io:
                IMGTerminal(IMG(io)).start()
        else:
            raise Exception('Unsupport type.')
