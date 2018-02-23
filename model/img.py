from io import FileIO, SEEK_CUR

from util.io_helper import IOHelper

FILE_MAGIC_OLD = 'Neople Image File'
FILE_MAGIC = 'Neople Img File'

FILE_VERSION_1 = 1
FILE_VERSION_2 = 2
FILE_VERSION_3 = 3
FILE_VERSION_4 = 4
FILE_VERSION_5 = 5
FILE_VERSION_6 = 6

IMAGE_FORMAT_1555 = 14
IMAGE_FORMAT_4444 = 15
IMAGE_FORMAT_8888 = 16
IMAGE_FORMAT_LINK = 17
IMAGE_FORMAT_DXT_1 = 18
IMAGE_FORMAT_DXT_3 = 19
IMAGE_FORMAT_DXT_5 = 20

PIX_SIZE = {
    IMAGE_FORMAT_1555: 2,
    IMAGE_FORMAT_4444: 2,
    IMAGE_FORMAT_8888: 4,
    IMAGE_FORMAT_DXT_1: 2,
    IMAGE_FORMAT_DXT_3: 2,
    IMAGE_FORMAT_DXT_5: 4,
}

ZIP_TYPE_NONE = 5
ZIP_TYPE_ZLIB = 6
ZIP_TYPE_DDS_ZLIB = 7


class IMG:
    def __init__(self, io):
        self._io = io  # type: FileIO
        self._images = None  # type: dict
        self._dds_images = None  # type: dict
        self._version = None
        self._color_board = None  # type: dict
        self._color_boards = None  # type: dict

        self._open()

    def _open_offset_count(self):
        io = self._io
        images = self._images

        # behind header.
        offset = io.tell()
        for i in images:
            image = images[i]
            if image['format'] != IMAGE_FORMAT_LINK:
                image['offset'] = offset
                offset += image['size']

    def _open_images(self, count):
        io = self._io
        images = {}

        for i in range(count):
            image = {}

            [fmt] = IOHelper.read_struct(io, '<i')
            image['format'] = fmt

            if fmt == IMAGE_FORMAT_LINK:
                [link] = IOHelper.read_struct(io, '<i')
                image['link'] = link
            else:
                zip_type, w, h, size, x, y, mw, mh = IOHelper.read_struct(io, '<8i')

                # fix size to real size.
                if zip_type == ZIP_TYPE_NONE:
                    size = w * h * PIX_SIZE[fmt]

                image['zip_type'] = zip_type
                image['w'] = w
                image['h'] = h
                image['offset'] = None
                image['data'] = None
                image['size'] = size
                image['x'] = x
                image['y'] = y
                image['mw'] = mw
                image['mh'] = mh

                if self._version == FILE_VERSION_5:
                    keep_1, dds_index, lx, ly, rx, ry, keep_2 = IOHelper.read_struct(io, '<7i')
                    image['keep_1'] = keep_1
                    image['dds_index'] = dds_index
                    image['left'] = lx
                    image['top'] = ly
                    image['right'] = rx
                    image['bottom'] = ry
                    image['keep_2'] = keep_2
                elif self._version == FILE_VERSION_1:
                    images[i]['offset'] = io.tell()
                    io.seek(size, SEEK_CUR)

            images[i] = image

        self._images = images

    @staticmethod
    def _open_color_board(io):
        [count] = IOHelper.read_struct(io, 'i')

        colors = {}
        for i in range(count):
            colors[i] = IOHelper.read_struct(io, '<4B')

        return colors

    def _open_dds_images(self, dds_count):
        io = self._io

        dds_images = {}
        for i in range(dds_count):
            version, fmt, index, raw_size, dds_size, w, h = IOHelper.read_struct(io, '<7i')
            dds_images[i] = {
                'version': version,
                'format': fmt,
                'index': index,
                'raw_size': raw_size,
                'dds_size': dds_size,
                'w': w,
                'h': h,
            }

        self._dds_images = dds_images

    def _open(self):
        io = self._io
        io.seek(0)

        magic = IOHelper.read_ascii_string(io, 18)
        if magic == FILE_MAGIC or magic == FILE_MAGIC_OLD:
            if magic == FILE_MAGIC:
                # head_size without version,count... keep: 0
                [head_size, keep] = IOHelper.read_struct(io, '<2i')
            else:
                # unknown.
                io.seek(6, SEEK_CUR)

            [version, count] = IOHelper.read_struct(io, '<2i')
            self._version = version

            # single color board.
            if version == FILE_VERSION_4:
                self._color_board = IMG._open_color_board(io)

            # multiple color board.
            if version == FILE_VERSION_6:
                color_boards = {}

                [colors_count] = IOHelper.read_struct(io, 'i')
                for i in range(colors_count):
                    color_boards[i] = IMG._open_color_board(io)

                self._color_boards = color_boards

            if version == FILE_VERSION_1 or version == FILE_VERSION_2 or version == FILE_VERSION_4 or version == FILE_VERSION_6:
                self._open_images(count)

            # dds image.
            if version == FILE_VERSION_5:
                dds_count, img_size = IOHelper.read_struct(io, '<2i')
                self._color_board = IMG._open_color_board(io)
                self._open_dds_images(dds_count)
                self._open_images(count)

            if version != FILE_VERSION_1:
                self._open_offset_count()
        else:
            raise Exception('Not NPK File.')

    @property
    def color_board(self):
        return self._color_board

    @property
    def color_boards(self):
        return self._color_boards

    @property
    def images(self):
        if self._images is not None:
            return list(self._images.keys())

    @property
    def dds_images(self):
        if self._dds_images is not None:
            return list(self._dds_images.keys())

    @property
    def version(self):
        return self._version
