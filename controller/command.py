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
        self.bind_function('extract', lambda file, name: common.write_file(file, npk.load_file(name)), {
            'file': {'type': str, 'help': 'save file path.'},
            'name': {'type': str, 'help': 'file name in file list.'},
        }, 'extract img file.')
        self.bind_function('open', self.open, {
            'type': {'type': str, 'help': 'open file type, img/ogg'},
            'file': {'type': str, 'help': 'file name in file list.'},
        }, 'open a file in file list.')

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


class IMGTerminal(Terminal):
    def __init__(self, img: IMG):
        super().__init__('OjoEx[IMG]> ')
        self._img = img

        self.bind_function('version', lambda: print(img.version), {}, 'print IMG version.')
        self.bind_function('images', lambda: print(img.images), {}, 'print image list.')
        self.bind_function('info', self.info, {
            'index': {'type': int, 'null': True, 'help': 'image index in image list'},
        }, 'print image info.')
        self.bind_function('color_board', lambda: print(img.color_board), {}, 'print color_board.')
        self.bind_function('color_boards', lambda: print(img.color_boards), {}, 'print color_boards.')
        self.bind_function('extract', lambda file, index, color_board_index: common.write_file(file, img.build(index,
                                                                                                               color_board_index)),
                           {
                               'file': {'type': str, 'help': 'save file path.'},
                               'index': {'type': int, 'help': 'image index in image list'},
                               'color_board_index': {'type': int, 'null': True,
                                                     'help': 'color_board_index in color_board list'},
                           }, 'extract png file.')

    def info(self, index=None):
        img = self._img
        if index is not None:
            print(img.info(index))
        else:
            for i in img.images:
                print(img.info(i))


class OGGTerminal(Terminal):
    def __init__(self, ogg: Bass):
        self._ogg = ogg
        super().__init__('OjoEx[OGG]> ')
        ogg.get_lentime()
        self.bind_function('set_loop', ogg.set_loop, {
            'loop': {'type': bool, 'help': 'is loop.'}
        }, 'sound loop play.')
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
    def __init__(self):
        self._term = Terminal('OjoDnfExtractor> ')
        self._term.bind_function('open', self.open, {
            'type': {'type': str, 'help': 'open file type, img/npk'},
            'file': {'type': str, 'help': 'open file path'},
        }, 'open a file.')
        Bass.init()

    def start(self, args):
        self._term.start()
        Bass.free()

    def open(self, type, file):
        if type == 'npk':
            with open(file, 'rb+') as io:
                NPKTerminal(NPK(io)).start()
        elif type == 'img':
            with open(file, 'rb+') as io:
                IMGTerminal(IMG(io)).start()
        else:
            raise Exception('Unsupport type.')
