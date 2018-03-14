from ctypes import c_float
from os.path import getsize

from .pybass import BASS_Init, BASS_Free, BASS_StreamCreateFile, BASS_StreamFree, BASS_ChannelPlay, \
    BASS_ChannelPause, \
    BASS_ChannelStop, BASS_ChannelGetPosition, BASS_ChannelSetPosition, BASS_ChannelGetLength, \
    BASS_ChannelGetAttribute, BASS_ChannelSetAttribute, BASS_ATTRIB_VOL, BASS_ATTRIB_FREQ, BASS_SAMPLE_LOOP, \
    BASS_GetVolume, \
    BASS_SetVolume, \
    BASS_ChannelSeconds2Bytes, BASS_GetVersion, BASS_ChannelFlags


class Bass:
    stat_dict = {0: 'stop', 1: 'play', 3: 'pause'}
    device = 0
    freq = 0

    @staticmethod
    def init(device=-1, freq=44100, flags=0, hwnd=0):
        Bass.device = device
        Bass.freq = freq
        res = BASS_Init(device, freq, flags, hwnd, 0)  # type:bool
        return res

    @staticmethod
    def free():
        res = BASS_Free()  # type:bool
        return res

    @staticmethod
    def get_volume_global():
        res = BASS_GetVolume()  # type:float
        return res

    @staticmethod
    def set_volume_global(vol):
        res = BASS_SetVolume(vol)  # type:bool
        return res

    @staticmethod
    def get_ver():
        res = BASS_GetVersion()  # type:int
        return res

    def __init__(self, path):
        mem = type(path) == bytes
        if mem:
            size = len(path)
        elif type(path) == str:
            size = getsize(path)
            path = bytes(path, encoding='utf8')
        else:
            raise Exception('Bass error:Unsupport type.')

        self._stream = BASS_StreamCreateFile(mem, path, 0, size, 0)
        self._loop = False

    def get_loop(self):
        return self._loop

    def set_loop(self, loop=True):
        if loop:
            BASS_ChannelFlags(self._stream, BASS_SAMPLE_LOOP, BASS_SAMPLE_LOOP)
        else:
            BASS_ChannelFlags(self._stream, 0, BASS_SAMPLE_LOOP)
        self._loop = loop

    def play(self, replay=True):
        res = BASS_ChannelPlay(self._stream, replay)  # type:bool
        return res

    def pause(self):
        res = BASS_ChannelPause(self._stream)  # type:bool
        return res

    def stop(self):
        res = BASS_ChannelStop(self._stream)  # type:bool
        return res

    def get_playpos(self):
        res = BASS_ChannelGetPosition(self._stream, 0)  # type:int
        return res

    def set_playpos(self, pos):
        res = BASS_ChannelSetPosition(self._stream, pos, 0)  # type:bool
        return res

    def get_length(self):
        res = BASS_ChannelGetLength(self._stream, 0)  # type:int
        return res

    def get_status(self):
        """
        :return:0=stop,1=play,3=pause
        """
        res = BASS_ChannelGetLength(self._stream)  # type:int
        return Bass.stat_dict.get(res, 'unknown')

    def destroy(self):
        res = BASS_StreamFree(self._stream)  # type:bool
        return res

    def get_volume(self):
        res = c_float()
        BASS_ChannelGetAttribute(self._stream, BASS_ATTRIB_VOL, res)
        res = res.value  # type:float
        return res

    def set_volume(self, vol):
        res = BASS_ChannelSetAttribute(self._stream, BASS_ATTRIB_VOL, vol)  # type:bool
        return res

    def get_speed(self):
        res = c_float(44100)
        BASS_ChannelGetAttribute(self._stream, BASS_ATTRIB_FREQ, res)
        res = res.value / Bass.freq  # type:float
        return res

    def set_speed(self, speed):
        res = BASS_ChannelSetAttribute(self._stream, BASS_ATTRIB_FREQ, speed * Bass.freq)  # type:bool
        return res

    def get_playtime(self):
        return self.postosec(self.get_playpos())

    def set_playtime(self, sec):
        return self.set_playpos(self.sectopos(sec))

    def get_lentime(self):
        return self.postosec(self.get_length())

    def postosec(self, pos):
        res = BASS_ChannelSeconds2Bytes(self._stream, pos)  # type:float
        return res

    def sectopos(self, sec):
        res = BASS_ChannelSeconds2Bytes(self._stream, sec)  # type:int
        return res


if __name__ == '__main__':
    from time import sleep

    Bass.init()
    b = Bass('/Users/Hs/Projects/DNF_EX_Hs/output/sounds_char_creator/cr_ancient.ogg')
    b.set_speed(1.5)
    b.play()
    sleep(2)
