import json
import os
import sys
from io import BytesIO

from model.img import IMG
from model.npk import NPK

args = sys.argv[1:]
if len(args) >= 2:
    ip2 = args[0]
    output = args[1]
else:
    ip2 = input("input ip2 path:")
    output = input("input output path:")

for i in os.listdir(ip2):
    if i[-4:].lower() == '.npk':
        with open('%s/%s' % (ip2, i), 'rb') as io_npk:
            print('extracting npk: %s' % i)
            npk = NPK(io_npk)
            for n in npk.files:
                info_img = npk.info(n)
                dirname, filename = os.path.split(info_img['name'])
                dirname = '%s/%s' % (output, dirname)
                os.makedirs(dirname, exist_ok=True)

                print('[%s]extracting img: %s' % (i, filename))
                data = npk.load_file(n)
                try:
                    with BytesIO(data) as io_img:
                        img = IMG(io_img)
                        il = len(img.images)

                        pos_info = []
                        for m in range(il):
                            info_image = img.info(m)
                            pos_info.append({'x': info_image['x'], 'y': info_image['y']})
                        with open('%s/%s' % (dirname, 'info.json'), 'w') as io:
                            json.dump(pos_info, io, ensure_ascii=False)

                        cbl = len(img.color_boards)
                        if cbl > 0:
                            for m in range(cbl):
                                for a in range(il):
                                    data_png = img.build(a, m)
                                    os.makedirs('%s/%d' % (dirname, m), exist_ok=True)
                                    with open('%s/%d/%d.png' % (dirname, m, a), 'wb') as io_png:
                                        io_png.write(data_png)
                        else:
                            for a in range(il):
                                data_png = img.build(a)
                                with open('%s/%d.png' % (dirname, a), 'wb') as io_png:
                                    io_png.write(data_png)
                except Exception as e:
                    print(e)
