from PySide6.QtWidgets import QWidget, QScrollArea, QMenu
from PySide6.QtGui import QGuiApplication, QShortcut, QKeySequence, QActionGroup, Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent, QContextMenuEvent
from PySide6.QtGui import QPainter, QPen, QColor, QImage
from PySide6.QtCore import Slot, QEvent, QPoint, QPointF, QRect, QRectF, QSizeF, Qt
from ImageWidget import ImageWidget
from enum import IntEnum


class _LeftButtonMode(IntEnum):
    Paint = 1
    Move = 2


class EditorWidget(QScrollArea):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._image_widget = ImageWidget(self)
        self.setWidget(self._image_widget)
        self.setAlignment(Qt.AlignCenter)
        self._horz_scroll_bar = self.horizontalScrollBar()
        self._vert_scroll_bar = self.verticalScrollBar()
        self._clipboard = QGuiApplication.clipboard()
        self._source_image = None
        self._image = None
        self._last_move_pos = None
        self._set_scale_factor(1.0)
        paste_shortcut = QShortcut(QKeySequence(QKeySequence.Paste), self)
        paste_shortcut.activated.connect(self._on_paste_shortcut)
        copy_shortcut = QShortcut(QKeySequence(QKeySequence.Copy), self)
        copy_shortcut.activated.connect(self._on_copy_shortcut)

        self._context_menu = QMenu(self)

        self._context_menu.addSection("Left Button Mode")
        mode_action_group = QActionGroup(self)
        self._paint_mode_action = self._context_menu.addAction("Paint")
        self._paint_mode_action.setCheckable(True)
        self._paint_mode_action.setChecked(True)
        mode_action_group.addAction(self._paint_mode_action)
        self._move_mode_action = self._context_menu.addAction("Move")
        self._move_mode_action.setCheckable(True)
        mode_action_group.addAction(self._move_mode_action)

        self._context_menu.addSection("Pen Width")
        self._pen_width_action_group = QActionGroup(self)
        for width in (2, 3, 5, 7, 10, 14, 20):
            action = self._context_menu.addAction(str(width) + " px")
            action.setData(width)
            action.setCheckable(True)
            self._pen_width_action_group.addAction(action)
            if width == 5:
                action.setChecked(True)

        self._context_menu.addSeparator()
        clear_action = self._context_menu.addAction("Clear")
        clear_action.triggered.connect(self._clear)

    def _set_scale_factor(self, factor: float) -> None:
        self._scale_factor = factor
        self._image_widget.set_scale_factor(factor)

    @Slot()
    def _on_paste_shortcut(self):

        mime_data = self._clipboard.mimeData()
        if mime_data.hasImage():
            image = self._clipboard.image()
            if not image.isNull():
                self._set_scale_factor(1.0)
                self._source_image = image
                self._restore_image()

    @Slot()
    def _on_copy_shortcut(self):

        if self._has_image():
            self._clipboard.setImage(self._image)

    @Slot()
    def _clear(self):
        if (self._source_image is not None) and (not self._source_image.isNull()):
            self._restore_image()

    def _restore_image(self):
        self._image = QImage(self._source_image)
        self._image_widget.set_image(self._image)
        self._image_widget.resize(self._image.size())

    def viewportEvent(self, event: QEvent) -> bool:

        if event.type() == QEvent.MouseButtonPress:
            self._handle_mouse_press_event(event)
        elif event.type() == QEvent.MouseButtonRelease:
            self._handle_mouse_release_event(event)
        elif event.type() == QEvent.MouseMove:
            self._handle_mouse_move_event(event)
        elif event.type() == QEvent.Wheel:
            self._handle_wheel_event(event)
        elif event.type() == QEvent.ContextMenu:
            self._handle_context_menu_event(event)
        else:
            return False
        return True

    def _is_moving(self) -> bool:
        return self._last_move_pos is not None

    def _left_button_mode(self) -> _LeftButtonMode:
        if self._paint_mode_action.isChecked():
            return _LeftButtonMode.Paint
        return _LeftButtonMode.Move

    def _handle_mouse_press_event(self, event: QMouseEvent) -> None:

        if self._has_image() and (event.button() == Qt.LeftButton) and (event.buttons() == Qt.LeftButton):
            self._last_move_pos = event.pos()
        elif self._is_moving():
            self._last_move_pos = None

    def _handle_mouse_release_event(self, event: QMouseEvent) -> None:
        if (event.button() == Qt.LeftButton) and self._is_moving():
            self._last_move_pos = None

    def _get_pen_width(self) -> int:
        pen_width_action = self._pen_width_action_group.checkedAction()
        if pen_width_action is None:
            return 0
        return round(int(pen_width_action.data()) * self._scale_factor)

    def _handle_mouse_move_event(self, event: QMouseEvent) -> None:

        if not self._has_image():
            return

        if not self._is_moving():
            return

        if self._left_button_mode() == _LeftButtonMode.Paint:
            painter = QPainter(self._image)
            viewport_top_left = QPointF(self._image_widget.mapFromParent(QPoint(0, 0))) / self._scale_factor
            viewport_size = QSizeF(self.viewport().size()) / self._scale_factor
            viewport_rect = QRectF(viewport_top_left, viewport_size)
            painter.setViewport(viewport_rect.toAlignedRect())
            painter.setWindow(self.viewport().rect())
            pen = QPen(QColor(255, 0, 0))
            pen.setWidth(self._get_pen_width())
            painter.setPen(pen)
            painter.drawLine(self._last_move_pos, event.pos())
            self._image_widget.update()
        else:
            offset = event.pos() - self._last_move_pos
            self._horz_scroll_bar.setValue(self._horz_scroll_bar.value() - offset.x())
            self._vert_scroll_bar.setValue(self._vert_scroll_bar.value() - offset.y())
        self._last_move_pos = event.pos()

    def _handle_wheel_event(self, event: QWheelEvent) -> None:

        if not self._has_image():
            super().wheelEvent(event)
            return

        angle_delta_y = event.angleDelta().y()

        if angle_delta_y == 0:
            super().wheelEvent(event)
            return

        scale_factor_factor = 1.1
        if angle_delta_y < 0:
            scale_factor_factor = 1.0 / scale_factor_factor
        old_center = self._image_widget.mapFromParent(self.viewport().rect().center())
        self._set_scale_factor(self._scale_factor * scale_factor_factor)
        self._image_widget.resize(self._image.size() * self._scale_factor)
        new_center = old_center * scale_factor_factor
        offset = new_center - old_center
        self._horz_scroll_bar.setValue(self._horz_scroll_bar.value() + offset.x())
        self._vert_scroll_bar.setValue(self._vert_scroll_bar.value() + offset.y())

    def _handle_context_menu_event(self, event: QContextMenuEvent) -> None:
        self._context_menu.exec_(event.globalPos())

    def _has_image(self) -> bool:
        return (self._image is not None) and (not self._image.isNull())
