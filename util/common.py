from io import BytesIO

from PIL import Image
from PIL.DdsImagePlugin import DdsImageFile
from PyQt5.QtWidgets import QTableWidgetItem

from util.io_helper import IOHelper


def zfill_bytes(data, size):
    fill_size = size - len(data)
    if fill_size > 0:
        data += b'\x00' * fill_size
    return data


def dds_to_png(data):
    with BytesIO(data) as io_dds:
        dds_file = DdsImageFile(io_dds)
        with BytesIO() as io_png:
            dds_file.save(io_png, 'png')
            data_png = IOHelper.read_range(io_png)

    return data_png


def raw_to_png(data, w, h):
    raw_img = Image.frombytes('RGBA', (w, h), data)

    with BytesIO() as io_png:
        raw_img.save(io_png, 'png')
        data_png = IOHelper.read_range(io_png)

    return data_png


def write_file(path, data):
    with open(path, 'bw') as io:
        io.write(data)


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


qtwi_str = lambda text: QTableWidgetItem(str(text))
