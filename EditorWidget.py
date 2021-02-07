from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPaintEvent, QPainter, QImage, QWheelEvent
from PySide6.QtCore import QSize, QSizeF, QRectF, QPointF, Signal


class EditorWidget(QWidget):

    scaled = Signal(float)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self._image = None
        self._scale_factor = 1.0

    def set_image(self, image: QImage) -> None:
        # print("EditorWidget.set_image:", image)
        self._image = image
        self._update_size()

    def paintEvent(self, event: QPaintEvent) -> None:

        if self._image is None:
            super().paintEvent(event)
        else:
            painter = QPainter(self)
            target_size = QSizeF(self._image.size()) * self._scale_factor
            target_rect = QRectF(QPointF(0, 0), target_size)
            source_rect = QRectF(self._image.rect())
            painter.drawImage(target_rect, self._image, source_rect)

    def wheelEvent(self, event: QWheelEvent) -> None:

        angle_delta_y = event.angleDelta().y()

        if angle_delta_y == 0:
            super().wheelEvent(event)
            return

        scale_factor_factor = 1.1
        if angle_delta_y < 0:
            scale_factor_factor = 1.0 / scale_factor_factor
        self._scale_factor *= scale_factor_factor
        self._update_size()
        self.scaled.emit(scale_factor_factor)

    def sizeHint(self) -> QSize:

        if self._image is None:
            return QSize()
        return self._image.size() * self._scale_factor

    def _update_size(self):
        self.setFixedSize(self.sizeHint())
        self.updateGeometry()
        self.update()
