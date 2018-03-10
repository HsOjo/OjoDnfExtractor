from model.img import IMG
from model.npk import NPK
from util import common
from util.terminal import Terminal


class Command:
    def __init__(self):
        self._term = Terminal('OjoDnfExtractor> ')
        self._term.bind_function('open', self.open, {
            'type': {'type': str, 'help': 'open file type, img/npk'},
            'file': {'type': str, 'help': 'open file path'},
        }, 'open a file.')

    def start(self, args):
        self._term.start()

    def open(self, type, file):
        if type == 'npk':
            with open(file, 'rb+') as io:
                npk = NPK(io)
                term = Terminal('OjoEx[NPK]> ')
                term.bind_function('files', lambda: print(npk.files), {}, 'print files list.')
                term.bind_function('extract', lambda file, name: common.write_file(file, npk.load_file(name)), {
                    'file': {'type': str, 'help': 'save file path.'},
                    'name': {'type': str, 'help': 'file name in files list.'},
                }, 'extract img file.')
                term.start()
        elif type == 'img':
            with open(file, 'rb+') as io:
                img = IMG(io)
                term = Terminal('OjoEx[IMG]> ')
                term.bind_function('version', lambda: print(img.version), {}, 'print version.')
                term.bind_function('images', lambda: print(img.images), {}, 'print images list.')
                term.bind_function('info', lambda x: print(img.info(x)), {
                    'id': {'type': int, 'help': 'image id in images list'},
                }, 'print image info.')
                term.bind_function('color_board', lambda: print(img.color_board), {}, 'print color_board.')
                term.bind_function('color_boards', lambda: print(img.color_boards), {}, 'print color_boards.')
                term.bind_function('extract',
                                   lambda file, id, color_board_id: common.write_file(file,
                                                                                      img.build(id, color_board_id)), {
                                       'file': {'type': str, 'help': 'save file path.'},
                                       'id': {'type': int, 'help': 'image id in images list'},
                                       'color_board_id': {'type': int, 'null': True,
                                                          'help': 'color_board_id in color_boards list'},
                                   }, 'extract png file.')
                term.start()
        else:
            raise Exception('Unsupport type.')
