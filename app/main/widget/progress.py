from PyQt6.QtWidgets import QWidget

from app.res.widget.progress.self import Ui_ProgressWidget


class ProgressWidget(Ui_ProgressWidget, QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._cancel = False

        pb = self.pb_work
        pb.setMinimum(0)
        pb.setMaximum(100)

    def set_title(self, title):
        self.setWindowTitle(title)

    def set_value(self, value):
        pb = self.pb_work
        min_, max_ = pb.minimum(), pb.maximum()
        if max_ != min_:
            percent = (value - min_) / (max_ - min_) * 100
        else:
            percent = 1
        pb.setValue(value)
        self.l_progress.setText('%d/%d (%d%%)' % (value, max_, percent))

    def set_min(self, value):
        self.pb_work.setMinimum(value)

    def set_max(self, value):
        self.pb_work.setMaximum(value)

    @property
    def cancel(self):
        return self._cancel

    def closeEvent(self, QCloseEvent):
        self._cancel = True
        # QCloseEvent.ignore()
