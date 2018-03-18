from lib.bass import Bass
from util.terminal import Terminal


class OGGTerminal(Terminal):
    def __init__(self, ogg: Bass):
        self._ogg = ogg
        super().__init__('OjoEx[OGG]> ')
        ogg.get_lentime()
        self.bind_function('set_loop', ogg.set_loop, {
            '_loop': {'type': bool, 'help': 'is _loop.'}
        }, 'sound _loop play.')
        self.bind_function('play', ogg.play, {
            'replay': {'type': bool, 'null': True, 'help': 'is replay.'}
        }, 'play sound.')
        self.bind_function('pause', ogg.pause, {}, 'pause sound.')
        self.bind_function('stop', ogg.stop, {}, 'stop sound.')
        self.bind_function('get_volume', lambda: print(ogg.get_volume()), {}, 'get volume.')
        self.bind_function('set_volume', ogg.set_volume, {
            'volume': {'type': float, 'help': 'volume size.'}
        }, 'change sound volume.')
        self.bind_function('get_speed', lambda: print(ogg.get_speed()), {}, 'get speed.')
        self.bind_function('set_speed', ogg.set_speed, {
            'speed': {'type': float, 'help': 'speed value.'}
        }, 'change sound speed.')
        self.bind_function('get_playtime', lambda: print(ogg.get_playtime()), {}, 'get time of play progress.')
        self.bind_function('set_playtime', ogg.set_playtime, {
            'playtime': {'type': float, 'help': 'time of play progress.'}
        }, 'change sound play time.')
        self.bind_function('get_lentime', lambda: print(ogg.get_lentime()), {}, 'get time of sound length.')
