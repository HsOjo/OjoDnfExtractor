from io import FileIO

from util.common import *
from util.io_helper import IOHelper

HEADER = 'NeoplePack_Bill'
C_DECORD_FLAG = bytes('puchikon@neople dungeon and fighter %s\x00' % ('DNF' * 73), encoding='ascii')


class NPK:
    def __init__(self, io):
        self._io = io  # type: FileIO
        self._files = None  # type: dict

    def open(self):
        io = self._io

        header = IOHelper.read_ascii_string(io, 16)
        if header != HEADER:
            raise Exception('Not NPK File.')

        [count] = IOHelper.read_struct(io, 'i')

        files = {}
        for i in range(count):
            offset, size = IOHelper.read_struct(io, '<2i')
            name = NPK._decrypt_name(io.read(256)).decode('ascii')
            files[name] = {
                'offset': offset,
                'size': size,
                'data': None,
            }

        self._files = files

    def load(self, name):
        file = self._files[name]

        if file['data'] is not None:
            return False

        file['data'] = IOHelper.read_range(self._io, file['offset'], file['data'])
        return file['data']

    def _load_all(self):
        files = self._files

        for name in files:
            self.load(name)

        return files

    def save(self, io: FileIO = None):
        # load file data.
        files = self._load_all()

        if io is None:
            io = self._io

        # clean file.
        io.seek(0)
        io.truncate()

        IOHelper.write_ascii_string(io, HEADER)
        count = len(files)
        IOHelper.write_struct(io, 'i', count)

        # count file offset.
        offset = 20 + count * 264

        for i, k in enumerate(files):
            file = files[k]

            file['offset'] = offset
            file['size'] = len(file['data'])

            IOHelper.write_struct(io, '<2i', file['offset'], file['size'])
            name = NPK._decrypt_name(k.encode(encoding='ascii'))
            io.write(name)

            offset += file['size']

        for i, k in enumerate(files):
            file = files[k]

            io.seek(file['offset'])
            io.write(file['data'])

    @staticmethod
    def _decrypt_name(data):
        data = zfill_bytes(data, 256)
        result_list = [0] * 256

        for i in range(256):
            result_list[i] = data[i] ^ C_DECORD_FLAG[i]

        result = bytes(result_list)
        return result

    def __del__(self):
        self._io.close()
