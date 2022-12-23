from PyQt6.QtGui import QPaintEvent, QPainter, QPen, QColor, QPalette
from PyQt6.QtWidgets import QMainWindow, QColorDialog

from app.res.window.screen.self import Ui_ScreenWindow


class ScreenWindow(Ui_ScreenWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._texture = {'x': 0, 'y': 0, 'w': 0, 'h': 0, 'pixmap': None}
        self._rect = {'draw': False, 'color': QColor(255, 0, 0)}
        self._blend = QPainter.CompositionMode.CompositionMode_SourceOver
        self._background_color = QColor(200, 200, 200)

        self._blend_bind = {
            self.a_blend_normal: QPainter.CompositionMode.CompositionMode_SourceOver,
            self.a_blend_plus: QPainter.CompositionMode.CompositionMode_Plus,
        }

        self.w_canvas.paintEvent = self._w_canvas_paint_event
        self.a_rect_draw.triggered.connect(lambda: self.set_rect(draw=self.a_rect_draw.isChecked()))
        self.a_rect_color.triggered.connect(self._a_rect_color_triggered)
        self.a_blend_normal.triggered.connect(lambda: self.set_blend(self._blend_bind[self.a_blend_normal]))
        self.a_blend_plus.triggered.connect(lambda: self.set_blend(self._blend_bind[self.a_blend_plus]))
        self.a_bg_color.triggered.connect(self._a_bg_color_triggered)

    def _a_bg_color_triggered(self):
        color = QColorDialog().getColor(initial=self._background_color)
        self.set_background_color(color)

    def _a_rect_color_triggered(self):
        color = QColorDialog().getColor(initial=self._rect['color'])
        self.set_rect(color)

    def set_background_color(self, color):
        self._background_color = color
        self.w_canvas.setPalette(QPalette(color))

    def set_blend(self, blend_mode):
        blend_bind = self._blend_bind
        self._blend = blend_mode

        for menu, value in blend_bind.items():
            menu.setChecked(value == blend_mode)

        self.w_canvas.update()

    def set_canvas(self, w, h):
        # draw rect need +1px
        self.w_canvas.resize(w + 1, h + 1)
        self.w_canvas.update()

    def set_rect(self, color: QColor = None, draw=True):
        rect = self._rect
        if color is not None:
            rect['color'] = color
        rect['draw'] = draw
        self.a_rect_draw.setChecked(draw)
        self.w_canvas.update()

    def set_texture(self, x, y, w, h, pixmap):
        texture = self._texture
        texture['x'] = x
        texture['y'] = y
        texture['w'] = w
        texture['h'] = h
        texture['pixmap'] = pixmap
        self.w_canvas.update()
        self.show()

    def _w_canvas_paint_event(self, qpe: QPaintEvent):
        painter = QPainter(self.w_canvas)
        texture = self._texture
        rect = self._rect

        if not painter.isActive():
            painter.begin(self.w_canvas)
        if texture['pixmap'] is not None:
            x, y, w, h = texture['x'], texture['y'], texture['w'], texture['h']
            if rect['draw']:
                painter.setPen(QPen(rect['color']))
                painter.drawRect(x, y, w, h)
            painter.setCompositionMode(self._blend)
            painter.drawPixmap(x, y, w, h, texture['pixmap'])
        painter.end()
