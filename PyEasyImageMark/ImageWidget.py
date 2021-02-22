from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPaintEvent, QPainter, QPen, QColor, QImage, QMouseEvent, QCursor
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
        self.__image = None
        self.__reset()
        self.__pen_width = 5
        self.__paint_enabled = True

    def __reset(self) -> None:
        self.__scale_factor = 1.0
        self.__lines = []
        self.__current_line_set = None
        self.__last_pen_pos = None

    def set_image(self, image: QImage) -> None:
        self.__image = image
        self.__reset()
        self.resize(image.size())
        self.update()

    def set_scale_factor(self, factor: float) -> None:
        self.__scale_factor = factor
        if self.has_image():
            self.resize(self.__image.size() * self.__scale_factor)
            self.update()

    def get_scale_factor(self) -> float:
        return self.__scale_factor

    def set_pen_width(self, width: int) -> None:
        self.__pen_width = width

    def get_pen_width(self) -> int:
        return self.__pen_width

    def set_paint_enabled(self, enabled: bool) -> None:
        self.__paint_enabled = enabled
        if not enabled and self.__last_pen_pos is not None:
            self.__finish_paint(self.mapFromGlobal(QCursor.pos()))

    def is_paint_enabled(self) -> bool:
        return self.__paint_enabled

    def has_image(self) -> bool:
        return (self.__image is not None) and (not self.__image.isNull())

    def get_complex_image(self) -> QImage:

        if self.__image is None:
            return QImage()

        image = QImage(self.__image)
        painter = QPainter(image)
        for line_set in self.__lines:
            line_set.draw(painter)
        return image

    def clear(self) -> None:
        print("clear")
        self.__lines = []
        self.update()

    def remove_last_line(self) -> None:
        if self.__current_line_set is not None:
            self.__current_line_set = None
            self.__last_pen_pos = None
        if len(self.__lines) > 0:
            self.__lines.pop()
        self.update()

    def __get_target_pen_width(self) -> float:
        return self.__pen_width / self.__scale_factor

    def paintEvent(self, event: QPaintEvent) -> None:

        if self.__image is None:
            super().paintEvent(event)

        else:
            painter = QPainter(self)

            # Draw image
            target_size = QSizeF(self.__image.size()) * self.__scale_factor
            target_rect = QRectF(QPointF(0, 0), target_size)
            source_rect = QRectF(self.__image.rect())
            painter.drawImage(target_rect, self.__image, source_rect)

            # Draw lines
            for line_set in self.__lines:
                line_set.draw(painter, self.__scale_factor)

    def __add_line(self, pos: QPoint) -> None:
        line = _Line(self.__last_pen_pos / self.__scale_factor, pos / self.__scale_factor)
        self.__current_line_set.add_line(line)

    def __finish_paint(self, pos: QPoint) -> None:
        if self.__last_pen_pos is not None:
            self.__add_line(pos)
            self.__last_pen_pos = None
            self.__current_lines = None
            self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.__paint_enabled and (event.button() == Qt.LeftButton) and (event.buttons() == Qt.LeftButton):
            self.__last_pen_pos = event.pos()
            self.__current_line_set = _LineSet(self.__get_target_pen_width())
            self.__lines.append(self.__current_line_set)
        else:
            self.__finish_paint(event.pos())
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.__paint_enabled and self.__last_pen_pos is not None:
            pos = event.pos()
            self.__add_line(pos)
            self.__last_pen_pos = pos
            self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.__paint_enabled and self.__last_pen_pos is not None:
            self.__finish_paint(event.pos())
        else:
            super().mouseReleaseEvent(event)
