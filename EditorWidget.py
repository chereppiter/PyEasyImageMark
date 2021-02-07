from PySide6.QtWidgets import QWidget, QScrollArea
from PySide6.QtGui import QGuiApplication, QShortcut, QKeySequence, QMouseEvent, QWheelEvent, Qt
from PySide6.QtCore import Slot, QEvent
from ImageWidget import ImageWidget


class EditorWidget(QScrollArea):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._image_widget = ImageWidget(self)
        self.setWidget(self._image_widget)
        self.setAlignment(Qt.AlignCenter)
        self._horz_scroll_bar = self.horizontalScrollBar()
        self._vert_scroll_bar = self.verticalScrollBar()
        self._clipboard = QGuiApplication.clipboard()
        self._image = None
        self._last_move_pos = None
        self._set_scale_factor(1.0)
        insert_shortcut = QShortcut(QKeySequence(QKeySequence.Paste), self)
        insert_shortcut.activated.connect(self._on_paste_shortcut)

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
                self._image = image
                self._image_widget.set_image(image)
                self._image_widget.resize(image.size())

    def viewportEvent(self, event: QEvent) -> bool:

        if event.type() == QEvent.MouseButtonPress:
            self._handle_mouse_press_event(event)
        elif event.type() == QEvent.MouseButtonRelease:
            self._handle_mouse_release_event(event)
        elif event.type() == QEvent.MouseMove:
            self._handle_mouse_move_event(event)
        elif event.type() == QEvent.Wheel:
            self._handle_wheel_event(event)
        else:
            return False
        return True

    def _is_translating(self) -> bool:
        return self._last_move_pos is not None

    def _handle_mouse_press_event(self, event: QMouseEvent) -> None:

        if (event.button() == Qt.LeftButton) and (event.buttons() == Qt.LeftButton):
            self._last_move_pos = event.pos()
        elif self._is_translating():
            self._last_move_pos = None

    def _handle_mouse_release_event(self, event: QMouseEvent) -> None:
        if (event.button() == Qt.LeftButton) and self._is_translating():
            self._last_move_pos = None

    def _handle_mouse_move_event(self, event: QMouseEvent) -> None:

        if self._is_translating():
            offset = event.pos() - self._last_move_pos
            self._last_move_pos = event.pos()
            self._horz_scroll_bar.setValue(self._horz_scroll_bar.value() - offset.x())
            self._vert_scroll_bar.setValue(self._vert_scroll_bar.value() - offset.y())

    def _handle_wheel_event(self, event: QWheelEvent) -> None:

        if (self._image is None) or self._image.isNull():
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
