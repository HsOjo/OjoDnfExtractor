import os
from io import BytesIO

from lib.bass import Bass
from model.img import IMG
from model.npk import NPK
from util import common
from util.terminal import Terminal
from .img_terminal import IMGTerminal
from .ogg_terminal import OGGTerminal


class NPKTerminal(Terminal):
    def __init__(self, npk: NPK):
        super().__init__('OjoEx[NPK]> ')
        self._npk = npk

        self.bind_function('files', lambda: print(npk.files), {}, 'print file list.')
        self.bind_function('info', self.info, {
            'index': {'type': int, 'null': True, 'help': 'file index in file list'},
        }, 'print file info.')
        self.bind_function('open', self.open, {
            'type': {'type': str, 'help': 'open file type, img/ogg'},
            'file': {'type': str, 'help': 'file name in file list.'},
        }, 'open a file in file list.')
        self.bind_function('load_all', npk.load_all, {}, 'load all files.')
        self.bind_function('extract', lambda file, index: common.write_file(file, npk.load_file(index)), {
            'file': {'type': str, 'help': 'save file path.'},
            'index': {'type': int, 'help': 'file index in file list'},
        }, 'extract img file.')
        self.bind_function('extract_all', self.extract_all, {
            'dir': {'type': str, 'help': 'path of extract dir.'},
            'mode': {'type': str, 'null': True, 'help': 'mode with filename. choices: wodir(default), raw'},
        }, 'extract all files to directory.')

    def extract_all(self, extract_dir, mode='wodir'):
        npk = self._npk
        npk.load_all()
        os.makedirs(extract_dir, exist_ok=True)
        for i in npk.files:
            info = npk.info(i)
            [dirname, filename] = os.path.split(info['name'])
            data = npk.load_file(i)
            print('writing: %s' % filename)
            os.makedirs(extract_dir, exist_ok=True)
            if mode == 'raw':
                dir_ = extract_dir + '/%s' % dirname
                os.makedirs(dir_, exist_ok=True)
                path = '%s/%s' % (dir_, filename)
            elif mode == 'wodir':
                path = '%s/%s' % (extract_dir, filename)
            else:
                raise Exception('Unsupport mode: %s' % mode)
            common.write_file(path, data)

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
                info = npk.info(i)
                print(i, info)
