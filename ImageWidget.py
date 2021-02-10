from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPaintEvent, QPainter, QImage, QWheelEvent
from PyQt5.QtCore import QSize, QSizeF, QRectF, QPointF


class ImageWidget(QWidget):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._image = None
        self._scale_factor = 1.0

    def set_image(self, image: QImage) -> None:
        self._image = image
        self.update()

    def set_scale_factor(self, factor: float) -> None:
        self._scale_factor = factor
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:

        if self._image is None:
            super().paintEvent(event)
        else:
            painter = QPainter(self)
            target_size = QSizeF(self._image.size()) * self._scale_factor
            target_rect = QRectF(QPointF(0, 0), target_size)
            source_rect = QRectF(self._image.rect())
            painter.drawImage(target_rect, self._image, source_rect)

