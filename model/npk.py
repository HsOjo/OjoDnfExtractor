from io import FileIO

from util.io_helper import IOHelper

HEADER = 'NeoplePack_Bill'
C_DECORD_FLAG = bytes('puchikon@neople dungeon and fighter %s\x00' % ('DNF' * 73), encoding='ascii')


class NPK:
    def __init__(self, io: FileIO):
        self._io = io
        self._files = None  # type: dict

    def load(self):
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

    def save(self):
        io = self._io

        io.seek(0)
        io.truncate()

        IOHelper.write_ascii_string(io, HEADER)
        count = len(self._files)
        IOHelper.write_struct(io, 'i', count)

        for i in range(count):


    @staticmethod
    def _decrypt_name(data):
        result_list = [0] * 256

        for i in range(256):
            result_list[i] = data[i] ^ C_DECORD_FLAG[i]

        result = bytes(result_list)
        return result
