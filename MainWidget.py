from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PySide6.QtGui import QGuiApplication, QShortcut, QKeySequence, QMouseEvent, QWheelEvent, Qt
from PySide6.QtCore import Slot
from EditorWidget import EditorWidget


class MainWidget(QWidget):

    def __init__(self):
        super().__init__()

        self._scroll_area = QScrollArea(self)
        self._editor = EditorWidget(self._scroll_area)
        self._editor.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self._scroll_area.setWidget(self._editor)
        self._horz_scroll_bar = self._scroll_area.horizontalScrollBar()
        self._vert_scroll_bar = self._scroll_area.verticalScrollBar()
        content_layout = QVBoxLayout(self)
        content_layout.addWidget(self._scroll_area)
        self.setLayout(content_layout)

        self._clipboard = QGuiApplication.clipboard()

        insert_shortcut = QShortcut(QKeySequence(QKeySequence.Paste), self)
        insert_shortcut.activated.connect(self._on_paste_shortcut)

        self._last_move_pos = None

        self._editor.scaled.connect(self._on_editor_scaled)

    @Slot()
    def _on_paste_shortcut(self):

        mime_data = self._clipboard.mimeData()
        if mime_data.hasImage():
            image = self._clipboard.image()
            self._editor.set_image(image)

    def _is_translating(self) -> bool:
        return self._last_move_pos is not None

    def mousePressEvent(self, event: QMouseEvent) -> None:

        if (event.button() == Qt.LeftButton) and (event.buttons() == Qt.LeftButton):
            self._last_move_pos = event.pos()
        elif self._is_translating():
            self._last_move_pos = None

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if (event.button() == Qt.LeftButton) and self._is_translating():
            self._last_move_pos = None

    def mouseMoveEvent(self, event: QMouseEvent) -> None:

        if self._is_translating():
            offset = event.pos() - self._last_move_pos
            self._last_move_pos = event.pos()
            self._horz_scroll_bar.setValue(self._horz_scroll_bar.value() - offset.x())
            self._vert_scroll_bar.setValue(self._vert_scroll_bar.value() - offset.y())

    def wheelEvent(self, event: QWheelEvent) -> None:

        print("Wheel event")
        super().wheelEvent(event)

    def _on_editor_scaled(self, factor: float) -> None:
        # print("Scaled:", factor)
        self._horz_scroll_bar.setValue(self._horz_scroll_bar.value() * factor)
        self._vert_scroll_bar.setValue(self._vert_scroll_bar.value() * factor)
