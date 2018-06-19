import hashlib
from io import FileIO, BytesIO

from util import common
from util.io_helper import IOHelper

FILE_MAGIC = 'NeoplePack_Bill'
C_DECORD_FLAG = bytes('puchikon@neople dungeon and fighter %s\x00' % ('DNF' * 73), encoding='ascii')


class NPK:
    def __init__(self, io=None):
        self._io = io  # type: FileIO
        self._files = []

        if io is not None:
            self._open()

    def _open(self):
        io = self._io
        io.seek(0)

        magic = IOHelper.read_ascii_string(io, 16)
        if magic != FILE_MAGIC:
            raise Exception('Not NPK File.')

        [count] = IOHelper.read_struct(io, 'i')

        files = []
        for i in range(count):
            offset, size = IOHelper.read_struct(io, '<2i')
            name_data = NPK._decrypt_name(io.read(256))
            try:
                name = name_data.decode('euc_kr')
                name = name[:name.find('\x00')]
            except:
                name = name_data[:name_data.find(b'\x00')].decode('euc_kr')
                print('Bad Filename: ', name_data)

            file = {
                'name': name,
                'offset': offset,
                'size': size,
                'data': None,
            }
            files.append(file)

        self._files = files

    def from_data(self, data: list):
        """{ 'name': str/bytes, 'data': bytes}"""
        files = self._files
        files.clear()
        for i in data:
            files.append({'name': i['name'], 'data': i['data'], 'size': len(i['data'])})

    def to_data(self):
        """{ 'name': str/bytes, 'data': bytes}"""
        files = self._files
        data = []
        for file in files:
            data.append({'name': file['name'], 'data': file['data']})
        return data

    def load_file(self, index):
        file = self._files[index]

        if file['data'] is None:
            file['data'] = IOHelper.read_range(self._io, file['offset'], file['size'])

        return file['data']

    def load_all(self):
        files = self._files

        for i in range(len(files)):
            self.load_file(i)

    def save(self, io=None):
        # load all file data.
        self.load_all()
        files = self._files

        if io is None:
            io = self._io

        # clean file.
        io.seek(0)
        io.truncate()

        head_data = b''

        # build head in memory.
        with BytesIO() as io_head:
            IOHelper.write_ascii_string(io_head, FILE_MAGIC)
            count = len(files)
            IOHelper.write_struct(io_head, 'i', count)

            # count file offset.
            # magic(16) + count(4) + info(264 * n) + hash(32)
            offset = 52 + count * 264

            for file in files:
                file['offset'] = offset
                file['size'] = len(file['data'])
                IOHelper.write_struct(io_head, '<2i', file['offset'], file['size'])
                if isinstance(file['name'], str):
                    name_data = file['name'].encode(encoding='euc_kr')
                elif isinstance(file['name'], bytes):
                    name_data = file['name']
                else:
                    raise Exception('Filename type Error: %s(%s)' % (file['name'], type(file['name'])))
                name = NPK._decrypt_name(name_data)
                io_head.write(name)

                offset += file['size']

            head_data = IOHelper.read_range(io_head)

        io.write(head_data)
        # write hash.
        io.write(hashlib.sha256(head_data[:len(head_data) // 17 * 17]).digest())

        for file in files:
            io.seek(file['offset'])
            io.write(file['data'])

    def info(self, index):
        file = self._files[index]  # type: dict

        info = {}
        for k, v in file.items():
            if k != 'data' and 'keep' not in k:
                info[k] = v

        return info

    def set_info(self, index, key, value):
        file = self._files[index]  # type: dict
        file[key] = value

    def id_from_name(self, name):
        files = self._files
        for i in range(len(files)):
            file = files[i]
            if name == file['name']:
                return i

    def remove_file(self, index):
        self._files.pop(index)

    def replace_file(self, index, data):
        name = self._files[index]['name']
        self.remove_file(index)
        self.insert_file(index, name, data)

    def insert_file(self, index, name, data):
        file = {
            'name': name,
            'offset': None,
            'size': len(data),
            'data': data,
        }
        self._files.insert(index, file)

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
        files = self._files
        if files is not None:
            return list(range(len(files)))

    def __len__(self):
        return len(self._files)
