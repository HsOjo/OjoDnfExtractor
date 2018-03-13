import hashlib
from io import FileIO, BytesIO

from util import common
from util.io_helper import IOHelper

FILE_MAGIC = 'NeoplePack_Bill'
C_DECORD_FLAG = bytes('puchikon@neople dungeon and fighter %s\x00' % ('DNF' * 73), encoding='ascii')


class NPK:
    def __init__(self, io):
        self._io = io  # type: FileIO
        self._files = None  # type: dict

        self._open()

    def _open(self):
        io = self._io
        io.seek(0)

        magic = IOHelper.read_ascii_string(io, 16)
        if magic != FILE_MAGIC:
            raise Exception('Not NPK File.')

        [count] = IOHelper.read_struct(io, 'i')

        files = {}
        for i in range(count):
            offset, size = IOHelper.read_struct(io, '<2i')
            name = NPK._decrypt_name(io.read(256)).decode('ascii')
            name = name[:name.find('\x00')]
            files[name] = {
                'offset': offset,
                'size': size,
                'data': None,
            }

        self._files = files

    def load_file(self, name):
        file = self._files[name]

        if file['data'] is None:
            file['data'] = IOHelper.read_range(self._io, file['offset'], file['size'])

        return file['data']

    def load_file_all(self):
        files = self._files

        for name in files:
            self.load_file(name)

        return files

    def save(self, io=None):
        # load_file file data.
        files = self.load_file_all()

        if io is None:
            io = self._io

        # clean file.
        io.seek(0)
        io.truncate()

        # build head in memory.
        with BytesIO() as io_head:
            IOHelper.write_ascii_string(io_head, FILE_MAGIC)
            count = len(files)
            IOHelper.write_struct(io_head, 'i', count)

            # count file offset.
            # magic(16) + count(4) + info(264 * n) + hash(32)
            offset = 52 + count * 264

            for i, k in enumerate(files):
                file = files[k]

                file['offset'] = offset
                file['size'] = len(file['data'])

                IOHelper.write_struct(io_head, '<2i', file['offset'], file['size'])
                name = NPK._decrypt_name(k.encode(encoding='ascii'))
                io_head.write(name)

                offset += file['size']

            head_data = IOHelper.read_range(io_head)

        io.write(head_data)
        # write hash.
        io.write(hashlib.sha256(head_data[:len(head_data) // 17 * 17]).digest())

        for i, k in enumerate(files):
            file = files[k]

            io.seek(file['offset'])
            io.write(file['data'])

    @staticmethod
    def _decrypt_name(data):
        data = common.zfill_bytes(data, 256)
        result_list = [0] * 256

        for i in range(256):
            result_list[i] = data[i] ^ C_DECORD_FLAG[i]

        result = bytes(result_list)
        return result

    @property
    def files(self):
        if self._files is not None:
            return list(self._files.keys())

    def __del__(self):
        self._io.close()
