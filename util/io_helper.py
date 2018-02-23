import struct

from util.common import *


class IOHelper:
    @staticmethod
    def read_struct(io, format, zfill=True):
        struct_size = struct.calcsize(format)
        data = io.read(struct_size)
        if zfill:
            data = zfill_bytes(data, struct_size)

        result = struct.unpack(format, data)
        return result

    @staticmethod
    def read_ascii_string(io, max_size=-1):
        result = ''
        while max_size == -1 or len(result) < max_size:
            [char] = IOHelper.read_struct(io, 'B')
            if char == 0:
                break

            result += chr(char)
        return result

    @staticmethod
    def read_range(io, offset=0, size=-1):
        io.seek(offset)
        return io.read(size)

    @staticmethod
    def write_struct(io, format, *values):
        data = struct.pack(format, *values)
        return io.write(data)

    @staticmethod
    def write_ascii_string(io, content: str):
        data = content.encode('ascii') + b'\x00'
        return io.write(data)
