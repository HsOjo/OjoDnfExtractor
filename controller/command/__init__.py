import os

from model.img import IMG
from model.npk import NPK
from util.terminal import Terminal
from .img_terminal import IMGTerminal
from .npk_terminal import NPKTerminal


class Command:
    def __init__(self, args):
        self.args = args
        self._term = Terminal('OjoDnfExtractor> ')
        self._term.bind_function('open', Command.open, {
            'type': {'type': str, 'help': 'open file type, img/npk'},
            'file': {'type': str, 'help': 'open file path'},
        }, 'open a file.')

    def start(self):
        files = self.args.files
        if len(files) > 0:
            self.open_auto(files[1])
        else:
            self._term.start()
        return 0

    @staticmethod
    def open(type_, path):
        if type_ == 'npk':
            with open(path, 'rb+') as io:
                NPKTerminal(NPK(io)).start()
        elif type_ == 'img':
            with open(path, 'rb+') as io:
                IMGTerminal(IMG(io)).start()
        else:
            raise Exception('Unsupport type_.')

    @staticmethod
    def open_auto(path):
        if os.path.exists(path):
            [dir, file] = os.path.split(path)
            if file[-4:].lower() == '.npk':
                Command.open('npk', path)
            elif file[-4:].lower() == '.img':
                Command.open('img', path)
            else:
                raise Exception('Unknown file type.', file)
        else:
            raise Exception('File not exists: %s' % path)
