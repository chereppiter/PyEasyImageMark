from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPaintEvent, QPainter, QPen, QColor, QImage, QMouseEvent
from PyQt5.QtCore import QSizeF, QRectF, QPoint, QPointF, Qt


class _Line:

    def __init__(self, p1: QPointF, p2: QPointF) -> None:
        self._p1 = p1
        self._p2 = p2

    def draw(self, painter: QPainter, scale_factor: float = 1.0) -> None:
        painter.drawLine(self._p1 * scale_factor, self._p2 * scale_factor)


class _LineSet:

    def __init__(self, pen_width: float) -> None:
        self._pen_width = pen_width
        self._lines = []

    def add_line(self, line: _Line) -> None:
        self._lines.append(line)

    def draw(self, painter: QPainter, scale_factor: float = 1.0) -> None:
        pen = QPen(QColor(255, 0, 0))
        pen.setWidthF(self._pen_width * scale_factor)
        painter.setPen(pen)
        for line in self._lines:
            line.draw(painter, scale_factor)


class ImageWidget(QWidget):

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._image = None
        self._reset()
        self._pen_width = 5
        self._paint_enabled = True

    def _reset(self) -> None:
        self._scale_factor = 1.0
        self._lines = []
        self._current_line_set = None
        self._last_pen_pos = None

    def set_image(self, image: QImage) -> None:
        self._image = image
        self._reset()
        self.resize(image.size())
        self.update()

    def set_scale_factor(self, factor: float) -> None:
        self._scale_factor = factor
        if self.has_image():
            self.resize(self._image.size() * self._scale_factor)
            self.update()

    def get_scale_factor(self) -> float:
        return self._scale_factor

    def set_pen_width(self, width: int) -> None:
        self._pen_width = width

    def set_paint_enabled(self, enabled: bool) -> None:
        self._paint_enabled = enabled
        if not enabled and self._last_pen_pos is not None:
            self._finish_paint()

    def has_image(self) -> bool:
        return (self._image is not None) and (not self._image.isNull())

    def get_complex_image(self) -> QImage:

        if self._image is None:
            return QImage()

        image = QImage(self._image)
        painter = QPainter(image)
        for line_set in self._lines:
            line_set.draw(painter)
        return image

    def clear(self) -> None:
        print("clear")
        self._lines = []
        self.update()

    def _get_target_pen_width(self) -> float:
        return self._pen_width / self._scale_factor

    def paintEvent(self, event: QPaintEvent) -> None:

        if self._image is None:
            super().paintEvent(event)

        else:
            painter = QPainter(self)

            # Draw image
            target_size = QSizeF(self._image.size()) * self._scale_factor
            target_rect = QRectF(QPointF(0, 0), target_size)
            source_rect = QRectF(self._image.rect())
            painter.drawImage(target_rect, self._image, source_rect)

            # Draw lines
            for line_set in self._lines:
                line_set.draw(painter, self._scale_factor)

    def _add_line(self, pos: QPoint) -> None:
        line = _Line(self._last_pen_pos / self._scale_factor, pos / self._scale_factor)
        self._current_line_set.add_line(line)

    def _finish_paint(self, pos: QPoint) -> None:
        if self._last_pen_pos is not None:
            self._add_line(pos)
            self._last_pen_pos = None
            self._current_lines = None
            self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self._paint_enabled:
            super().mousePressEvent(event)
            return
        if (event.button() == Qt.LeftButton) and (event.buttons() == Qt.LeftButton):
            self._last_pen_pos = event.pos()
            self._current_line_set = _LineSet(self._get_target_pen_width())
            self._lines.append(self._current_line_set)
        else:
            self._finish_paint(event.pos())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self._paint_enabled:
            super().mouseMoveEvent(event)
            return
        if self._last_pen_pos is not None:
            pos = event.pos()
            self._add_line(pos)
            self._last_pen_pos = pos
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if not self._paint_enabled:
            super().mouseReleaseEvent(event)
            return
        if self._last_pen_pos is not None:
            self._finish_paint(event.pos())
