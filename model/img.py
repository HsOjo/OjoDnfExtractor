import zlib
from io import FileIO, BytesIO, SEEK_CUR

from PIL.PngImagePlugin import PngImageFile

from util import common
from util.io_helper import IOHelper
from .nx_color import NXColor

FILE_MAGIC_OLD = 'Neople Image File'
FILE_MAGIC = 'Neople Img File'

FILE_VERSION_1 = 1
FILE_VERSION_2 = 2
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

IMAGE_FORMATS_RAW = (IMAGE_FORMAT_1555, IMAGE_FORMAT_4444, IMAGE_FORMAT_8888)
IMAGE_FORMATS_DDS = (IMAGE_FORMAT_DXT_1, IMAGE_FORMAT_DXT_3, IMAGE_FORMAT_DXT_5)

PIX_SIZE = {
    IMAGE_FORMAT_1555: 2,
    IMAGE_FORMAT_4444: 2,
    IMAGE_FORMAT_8888: 4,
    IMAGE_FORMAT_DXT_1: 2,
    IMAGE_FORMAT_DXT_3: 2,
    IMAGE_FORMAT_DXT_5: 4,
}

IMAGE_EXTRA_NONE = 5
IMAGE_EXTRA_ZLIB = 6
IMAGE_EXTRA_MAP_ZLIB = 7

IMAGE_FORMAT_TEXT = {
    IMAGE_FORMAT_1555: '1555',
    IMAGE_FORMAT_4444: '4444',
    IMAGE_FORMAT_8888: '8888',
    IMAGE_FORMAT_LINK: 'link',
    IMAGE_FORMAT_DXT_1: 'dxt_1',
    IMAGE_FORMAT_DXT_3: 'dxt_3',
    IMAGE_FORMAT_DXT_5: 'dxt_5',
}

IMAGE_EXTRA_TEXT = {
    IMAGE_EXTRA_NONE: 'none',
    IMAGE_EXTRA_ZLIB: 'zlib',
    IMAGE_EXTRA_MAP_ZLIB: 'map_zlib',
}


class IMG:
    def __init__(self, io=None):
        self._io = io  # type: FileIO
        self._images = []
        self._map_images = []
        self._version = FILE_VERSION_2
        self._color_board = []
        self._color_boards = []

        if io is not None:
            self._open()

    def _open_images(self, count):
        io = self._io
        version = self._version
        images = []

        for i in range(count):
            image = {}

            [fmt] = IOHelper.read_struct(io, '<i')
            image['format'] = fmt

            if fmt == IMAGE_FORMAT_LINK:
                [link] = IOHelper.read_struct(io, '<i')
                image['link'] = link
            else:
                extra, w, h, size, x, y, mw, mh = IOHelper.read_struct(io, '<8i')

                # fix size to real size.
                if (version == FILE_VERSION_1 or version == FILE_VERSION_2) and extra == IMAGE_EXTRA_NONE:
                    size = w * h * PIX_SIZE[fmt]

                image['extra'] = extra
                image['w'] = w
                image['h'] = h
                image['size'] = size
                image['x'] = x
                image['y'] = y
                image['mw'] = mw
                image['mh'] = mh
                # temp
                image['data'] = None

                if extra == IMAGE_EXTRA_MAP_ZLIB:
                    keep_1, map_index, lx, ly, rx, ry, rotate = IOHelper.read_struct(io, '<7i')
                    image['keep_1'] = keep_1
                    image['map_index'] = map_index
                    image['left'] = lx
                    image['top'] = ly
                    image['right'] = rx
                    image['bottom'] = ry
                    # horizontal, vertical
                    image['rotate'] = rotate

                if self._version == FILE_VERSION_1:
                    image['offset'] = io.tell()
                    io.seek(size, SEEK_CUR)

            images.append(image)

        return images

    def _open_color_board(self):
        io = self._io

        [count] = IOHelper.read_struct(io, 'i')

        colors = []
        for i in range(count):
            color = IOHelper.read_struct(io, '<4B')
            colors.append(color)

        return colors

    def _open_map_images(self, map_count):
        io = self._io

        map_images = []
        for i in range(map_count):
            keep, fmt, index, data_size, raw_size, w, h = IOHelper.read_struct(io, '<7i')
            map_image = {
                'keep': keep,
                'format': fmt,
                'index': index,
                'data_size': data_size,
                'raw_size': raw_size,
                'w': w,
                'h': h,
                'data': None,
            }
            map_images.append(map_image)

        return map_images

    def _open(self):
        io = self._io
        io.seek(0)

        magic = IOHelper.read_ascii_string(io, 18)
        if magic == FILE_MAGIC or magic == FILE_MAGIC_OLD:
            if magic == FILE_MAGIC:
                # images_size without version,count,extra(color_board,map_images)...
                [images_size] = IOHelper.read_struct(io, 'i')
            else:
                # unknown.
                [unknown] = IOHelper.read_struct(io, 'h')
                images_size = 0

            # keep: 0
            [keep, version, img_count] = IOHelper.read_struct(io, '<3i')
            self._version = version

            if version == FILE_VERSION_4:
                # single color board.
                self._color_board = self._open_color_board()
            elif version == FILE_VERSION_5:
                # map image.
                map_count, file_size = IOHelper.read_struct(io, '<2i')
                self._color_board = self._open_color_board()
                self._map_images = self._open_map_images(map_count)
            elif version == FILE_VERSION_6:
                # multiple color board.
                color_boards = []

                [color_board_count] = IOHelper.read_struct(io, 'i')
                for i in range(color_board_count):
                    color_board = self._open_color_board()
                    color_boards.append(color_board)

                self._color_boards = color_boards

            images = self._open_images(img_count)
            self._images = images

            # count image offset.
            if version != FILE_VERSION_1:
                # behind header.
                if images_size != 0:
                    offset = images_size + 32
                else:
                    offset = io.tell()

                if version == FILE_VERSION_5:
                    map_images = self._map_images
                    for i in range(len(map_images)):
                        map_image = map_images[i]
                        map_image['offset'] = offset
                        offset += map_image['data_size']
                for i in range(len(images)):
                    image = images[i]
                    if image['format'] != IMAGE_FORMAT_LINK and image['extra'] != IMAGE_EXTRA_MAP_ZLIB:
                        image['offset'] = offset
                        offset += image['size']
        else:
            raise Exception('Not IMG File.')

    def load_image_map(self, index):
        io = self._io
        map_image = self._map_images[index]

        if map_image['data'] is not None:
            return map_image['data']

        data = IOHelper.read_range(io, map_image['offset'], map_image['data_size'])
        data = zlib.decompress(data)
        map_image['data'] = data

        return data

    def load_image(self, index):
        io = self._io
        image = self._images[index]

        if image['format'] == IMAGE_FORMAT_LINK:
            return None

        if image['data'] is not None:
            return image['data']

        data = IOHelper.read_range(io, image['offset'], image['size'])

        if image['extra'] == IMAGE_EXTRA_ZLIB:
            data = zlib.decompress(data)
        elif image['extra'] != IMAGE_EXTRA_NONE:
            raise Exception('Unknown Extra Type.', image['extra'])

        image['data'] = data

        return data

    def load_all(self):
        images = self._images
        map_images = self._map_images

        for i in range(len(images)):
            self.load_image(i)

        for i in range(len(map_images)):
            self.load_image_map(i)

    def _save_count_images_size(self):
        images = self._images
        size = 0

        for image in images:
            # format
            size += 4
            if image['format'] == IMAGE_FORMAT_LINK:
                # link
                size += 4
            else:
                # extra, w, h, size, x, y, mw, mh
                size += 32
                if image['extra'] == IMAGE_EXTRA_MAP_ZLIB:
                    # keep_1, map_index, left, top, right, bottom, rotate
                    size += 28

        return size

    def _save_count_file_size(self, images_size, images_data):
        map_images = self._map_images
        color_board = self._color_board
        color_boards = self._color_boards
        version = self._version

        size = 0
        if version == FILE_VERSION_1:
            # magic, unknown
            size += len(FILE_MAGIC_OLD) + 3
        else:
            # magic, images_size
            size += len(FILE_MAGIC) + 5

        # keep, version, img_count
        size += 12

        is_ver5 = version == FILE_VERSION_5

        if is_ver5:
            # map_count, img_size
            size += 8
            # keep, format, index, data_size, raw_size, w, h
            size += len(map_images) * 28

        if version == FILE_VERSION_4 or is_ver5:
            # color count.
            size += 4
            # colors size.
            size += len(color_board) * 4

        if version == FILE_VERSION_6:
            # color_boards_count
            size += 4
            for color_board_v6 in color_boards:
                # color count.
                size += 4
                # colors size.
                size += len(color_board_v6) * 4

        size += images_size

        for data in images_data:
            size += len(data)

        return size

    def save(self, io=None):
        self.load_all()
        images = self._images
        color_board = self._color_board
        color_boards = self._color_boards
        map_images = self._map_images
        version = self._version

        images_data = []

        # compress data, get size, add to data_list.
        if version == FILE_VERSION_5:
            for map_image in sorted(map_images):
                data = map_image['data']
                map_image['raw_size'] = len(data)
                data = zlib.compress(data)
                map_image['data_size'] = len(data)

                images_data.append(data)
        else:
            for image in images:
                if image['format'] != IMAGE_FORMAT_LINK:
                    data = image['data']
                    if image['extra'] == IMAGE_EXTRA_ZLIB or image['extra'] == IMAGE_EXTRA_MAP_ZLIB:
                        data = zlib.compress(data)
                    image['size'] = len(data)

                    images_data.append(data)

        images_size = self._save_count_images_size()
        file_size = self._save_count_file_size(images_size, images_data)

        if io is None:
            io = self._io

        io.seek(0)
        io.truncate()

        with BytesIO() as io_head:
            if version == FILE_VERSION_1:
                IOHelper.write_ascii_string(io_head, FILE_MAGIC_OLD)
                # TODO: unknown, now be zero.
                IOHelper.write_struct(io_head, 'h', 0)
            else:
                # images_size
                IOHelper.write_ascii_string(io_head, FILE_MAGIC)
                IOHelper.write_struct(io_head, 'i', images_size)

            # keep, version, img_count
            IOHelper.write_struct(io_head, '<3i', 0, version, len(images))

            is_ver5 = version == FILE_VERSION_5

            if is_ver5:
                # map_count, file_size
                IOHelper.write_struct(io_head, '<2i', len(map_images), file_size)

            if version == FILE_VERSION_4 or is_ver5:
                # color_count
                IOHelper.write_struct(io_head, 'i', len(color_board))
                for color in color_board:
                    # color
                    IOHelper.write_struct(io_head, '<4B', *color)

            if is_ver5:
                for map_image in map_images:
                    IOHelper.write_struct(io_head, '<7i', map_image['keep'], map_image['format'], map_image['index'],
                                          map_image['data_size'], map_image['raw_size'], map_image['w'], map_image['h'])

            if version == FILE_VERSION_6:
                # color_board count.
                IOHelper.write_struct(io_head, 'i', len(color_boards))
                for color_board_v6 in color_boards:
                    # color_count
                    IOHelper.write_struct(io_head, 'i', len(color_board_v6))
                    for color in color_board_v6:
                        # color
                        IOHelper.write_struct(io_head, '<4B', *color)

            for image in images:
                # format
                IOHelper.write_struct(io_head, 'i', image['format'])
                if image['format'] == IMAGE_FORMAT_LINK:
                    # link
                    IOHelper.write_struct(io_head, 'i', image['link'])
                else:
                    # extra, w, h, size, x, y, mw, mh
                    IOHelper.write_struct(io_head, '<8i', image['extra'], image['w'], image['h'], image['size'],
                                          image['x'], image['y'], image['mw'], image['mh'])
                    if image['extra'] == IMAGE_EXTRA_MAP_ZLIB:
                        # keep_1, map_index, left, top, right, bottom, rotate
                        IOHelper.write_struct(io_head, '<7i', image['keep_1'], image['map_index'], image['left'],
                                              image['top'], image['right'], image['bottom'], image['rotate'])

            head_data = IOHelper.read_range(io_head)

        io.write(head_data)

        for data in images_data:
            io.write(data)

    def build_map(self, index, box=None, rotate=0):
        map_image = self._map_images[index]

        data = self.load_image_map(index)
        if map_image['format'] in IMAGE_FORMATS_DDS:
            data = common.dds_to_png(data, box, rotate)
        else:
            data = IMG._nximg_to_raw(data, map_image['format'], map_image['w'], box)
            if box is not None:
                [l, t, r, b] = box
                w, h = r - l, b - t
            else:
                w, h = map_image['w'], map_image['h']
            data = common.raw_to_png(data, w, h, rotate)

        return data

    def build(self, index, color_board_index=0):
        image = self._images[index]

        if image['format'] == IMAGE_FORMAT_LINK:
            return self.build(image['link'], color_board_index)

        if image['extra'] == IMAGE_EXTRA_MAP_ZLIB:
            l, t, r, b = image['left'], image['top'], image['right'], image['bottom']
            data = self.build_map(image['map_index'], (l, t, r, b), image['rotate'])
        else:
            data = self.load_image(index)
            version = self._version

            if version == FILE_VERSION_1 or version == FILE_VERSION_2 or version == FILE_VERSION_5:
                data = IMG._nximg_to_raw(data, image['format'])
            elif version == FILE_VERSION_4:
                data = IMG._indexes_to_raw(data, self._color_board)
            elif version == FILE_VERSION_6:
                data = IMG._indexes_to_raw(data, self._color_boards[color_board_index])
            else:
                raise Exception('Unknown IMG Version.', version)

            data = common.raw_to_png(data, image['w'], image['h'])

        return data

    def info(self, index):
        images = self._images
        image = images[index]  # type: dict

        info = {}
        if image['format'] == IMAGE_FORMAT_LINK:
            if image['link'] < len(images):
                info.update(images[image['link']])
            else:
                print('link index out of range: %d' % image['link'])

        info.update(image)
        info.pop('data', None)

        return info

    def set_info(self, index, key, value):
        image = self._images[index]  # type: dict
        image[key] = value

    def remove_image(self, index):
        self._images.pop(index)

    def replace_image(self, index, data, image_format=IMAGE_FORMAT_8888):
        self.remove_image(index)
        self.insert_image(index, data, image_format)

    def insert_image(self, index, data, image_format=IMAGE_FORMAT_8888):
        version = self._version
        images = self._images

        image = {
            'format': image_format,
            'extra': IMAGE_EXTRA_NONE,
            'x': 0,
            'y': 0,
            'mw': 800,
            'mh': 600,
        }

        if version == FILE_VERSION_1 or version == FILE_VERSION_2:
            image['data'], image['w'], image['h'] = IMG._png_to_nximg(data, image_format)
            image['size'] = len(image['data'])
            if image['w'] > image['mw']:
                image['mw'] = image['w']
            if image['h'] > image['mh']:
                image['mh'] = image['h']
            if index == -1:
                index = len(images)
            images.insert(index, image)
        else:
            raise Exception('Unsupport file version: ver%s' % version)

    def info_map(self, index):
        map_image = self._map_images[index]  # type: dict

        info = map_image.copy()
        info.pop('data', None)

        return info

    def remove_map_image(self, index):
        self._map_images.pop(index)

    def replace_map_image(self, index, data):
        self.remove_map_image(index)
        self.insert_map_image(index, data)

    def insert_map_image(self, index, data):
        # TODO: insert map image.
        raise Exception('TODO: insert map image.')

    @staticmethod
    def _indexes_to_raw(data, color_board):
        with BytesIO(data) as io_indexes:
            with BytesIO() as io_raw:
                temp = IOHelper.read_struct(io_indexes, '<B', False)
                while temp is not None:
                    [index] = temp
                    IOHelper.write_struct(io_raw, '<4B', *color_board[index])
                    temp = IOHelper.read_struct(io_indexes, '<B', False)
                data_raw = IOHelper.read_range(io_raw)

        return data_raw

    @staticmethod
    def _nximg_to_raw(data, image_format, w=None, box=None):
        data_raw = bytes()
        ps = PIX_SIZE[image_format]

        with BytesIO(data) as io_nximg:
            with BytesIO() as io_raw:
                if image_format == IMAGE_FORMAT_1555:
                    if box is not None and w is not None:
                        [left, top, right, bottom] = box
                        for y in range(top, bottom):
                            o = y * w * ps
                            for x in range(left, right):
                                io_nximg.seek(o + x * ps)
                                temp = IOHelper.read_struct(io_nximg, '<2B', False)
                                if temp is not None:
                                    [v1, v2] = temp
                                    IOHelper.write_struct(io_raw, '<4B', *NXColor.from_1555(v1, v2))
                    else:
                        temp = IOHelper.read_struct(io_nximg, '<2B', False)
                        while temp is not None:
                            [v1, v2] = temp
                            IOHelper.write_struct(io_raw, '<4B', *NXColor.from_1555(v1, v2))

                            temp = IOHelper.read_struct(io_nximg, '<2B', False)
                elif image_format == IMAGE_FORMAT_4444:
                    if box is not None and w is not None:
                        [left, top, right, bottom] = box
                        for y in range(top, bottom):
                            o = y * w * ps
                            for x in range(left, right):
                                io_nximg.seek(o + x * ps)
                                temp = IOHelper.read_struct(io_nximg, '<2B', False)
                                if temp is not None:
                                    [v1, v2] = temp
                                    IOHelper.write_struct(io_raw, '<4B', *NXColor.from_4444(v1, v2))
                    else:
                        temp = IOHelper.read_struct(io_nximg, '<2B', False)
                        while temp is not None:
                            [v1, v2] = temp
                            IOHelper.write_struct(io_raw, '<4B', *NXColor.from_4444(v1, v2))

                            temp = IOHelper.read_struct(io_nximg, '<2B', False)
                elif image_format == IMAGE_FORMAT_8888:
                    if box is not None and w is not None:
                        [left, top, right, bottom] = box
                        for y in range(top, bottom):
                            o = y * w * ps
                            for x in range(left, right):
                                io_nximg.seek(o + x * ps)
                                temp = IOHelper.read_struct(io_nximg, '<4B', False)
                                if temp is not None:
                                    [b, g, r, a] = temp
                                    IOHelper.write_struct(io_raw, '<4B', r, g, b, a)
                    else:
                        temp = IOHelper.read_struct(io_nximg, '<4B', False)
                        while temp is not None:
                            [b, g, r, a] = temp
                            IOHelper.write_struct(io_raw, '<4B', r, g, b, a)

                            temp = IOHelper.read_struct(io_nximg, '<4B', False)
                else:
                    raise Exception('Unsupport Image Format.', image_format)

                data_raw = IOHelper.read_range(io_raw)

        return data_raw

    @staticmethod
    def _png_to_nximg(data, image_format):
        data_nximg = bytes()

        with BytesIO(data) as io_png:
            with BytesIO() as io_nximg:
                png = PngImageFile(io_png)
                w, h = png.width, png.height

                if image_format == IMAGE_FORMAT_1555:
                    for y in range(h):
                        for x in range(w):
                            [r, g, b, a] = png.getpixel((x, y))
                            IOHelper.write_struct(io_nximg, "<2B", *NXColor.to_1555(r, g, b, a))
                elif image_format == IMAGE_FORMAT_4444:
                    for y in range(h):
                        for x in range(w):
                            [r, g, b, a] = png.getpixel((x, y))
                            IOHelper.write_struct(io_nximg, "<2B", *NXColor.to_4444(r, g, b, a))
                elif image_format == IMAGE_FORMAT_8888:
                    for y in range(h):
                        for x in range(w):
                            [r, g, b, a] = png.getpixel((x, y))
                            IOHelper.write_struct(io_nximg, "<4B", b, g, r, a)
                else:
                    raise Exception('Unsupport image format: %s' % image_format)

                data_nximg = IOHelper.read_range(io_nximg)

        return data_nximg, w, h

    @property
    def color_board(self):
        return self._color_board

    @property
    def color_boards(self):
        return self._color_boards

    @property
    def images(self):
        images = self._images
        if images is not None:
            return list(range(len(images)))

    @property
    def map_images(self):
        map_images = self._map_images
        if map_images is not None:
            return list(range(len(map_images)))

    @property
    def version(self):
        return self._version
