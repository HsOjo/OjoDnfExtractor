from io import BytesIO

from PIL import Image
from PIL.DdsImagePlugin import DdsImageFile

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
