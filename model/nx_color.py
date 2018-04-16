class NXColor:
    @staticmethod
    def from_1555(v1, v2):
        b = v1 & 0x1f
        b = b << 3 | b >> 2
        g = (v1 >> 5) | (v2 & 3) << 3
        g = g << 3 | g >> 2
        r = (v2 >> 2) & 0x1f
        r = r << 3 | r >> 2
        a = v2 >> 7
        a = a * 0xff

        return r, g, b, a

    @staticmethod
    def to_1555(r, g, b, a):
        b = b >> 3
        g = g >> 3
        r = r >> 3
        a = a >> 7

        v1 = (g & 7) << 5 | b
        v2 = (a << 7) | (r << 2) | (g >> 3)

        return v1, v2

    @staticmethod
    def from_4444(v1, v2):
        b = (v1 & 0xf) << 4
        g = v1 & 0xf0
        r = (v2 & 0xf) << 4
        a = v2 & 0xf0

        return r, g, b, a

    @staticmethod
    def to_4444(r, g, b, a):
        v1 = g | b >> 4
        v2 = a | r >> 4

        return v1, v2
