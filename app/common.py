from io import BytesIO

from PIL import Image
from PIL.DdsImagePlugin import DdsImageFile
from PyQt6.QtWidgets import QTableWidgetItem

from .util.io_helper import IOHelper


def dds_to_png(data, box=None, rotate=0):
    with BytesIO(data) as io_dds:
        sprite = DdsImageFile(io_dds)
        if box is not None:
            sprite = sprite.crop(box)

        if rotate == 1:
            sprite = sprite.transpose(Image.ROTATE_90)

        with BytesIO() as io_png:
            sprite.save(io_png, 'png')
            data_png = IOHelper.read_range(io_png)

    return data_png


def raw_to_png(data, w, h, rotate=0):
    raw_image = Image.frombytes('RGBA', (w, h), data)

    if rotate == 1:
        raw_image = raw_image.transpose(Image.ROTATE_90)

    with BytesIO() as io_png:
        raw_image.save(io_png, 'png')
        data_png = IOHelper.read_range(io_png)

    return data_png


def write_file(path, data):
    with open(path, 'bw') as io:
        io.write(data)


def read_file(path):
    with open(path, 'br') as io:
        data = io.read()
    return data


# by musoucrow.
def param_split(s):
    lst = []
    sb = []
    n = len(s)
    i = 0
    j = 0

    def add_sb_to_lst():
        if len(sb) > 0:
            lst.append(''.join(sb))
            sb.clear()

    while i < n:
        if s[i] == ' ':
            pass
        elif s[i] != '"' and s[i] != "'":
            for j in range(i, n):
                if s[j] == ' ':
                    break

            j += 1

            for k in range(i, j):
                sb.append(s[k])

            add_sb_to_lst()
            i = j - 1
        else:
            for j in range(i + 1, n):
                if s[i] == s[j]:
                    break

            j += 1

            for k in range(i + 1, j):
                sb.append(s[k])

            add_sb_to_lst()
            i = j

        i += 1

    return lst


def qtwi_str(text=''):
    return QTableWidgetItem(str(text))


def get_filename_wo_ext(filename: str):
    return filename[:filename.rfind('.')]


def is_std_name(name: str):
    if name != name.strip():
        return False

    ext = name[-4:].lower()
    if ext != '.img' and ext != '.ogg':
        return False

    return True
