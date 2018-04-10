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
        self._term.start()
        return 0

    @staticmethod
    def open(type_, file):
        if type_ == 'npk':
            with open(file, 'rb+') as io:
                NPKTerminal(NPK(io)).start()
        elif type_ == 'img':
            with open(file, 'rb+') as io:
                IMGTerminal(IMG(io)).start()
        else:
            raise Exception('Unsupport type_.')
