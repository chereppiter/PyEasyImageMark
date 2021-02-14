from PyQt5.QtWidgets import (QWidget, QScrollArea, QMenu, QApplication,
                             QAction, QShortcut, QActionGroup)
from PyQt5.QtGui import QKeySequence, QMouseEvent, QWheelEvent, QContextMenuEvent
from PyQt5.QtCore import QEvent, Qt
from ImageWidget import ImageWidget


class EditorWidget(QScrollArea):

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._image_widget = ImageWidget(self)
        self.setWidget(self._image_widget)
        self.setAlignment(Qt.AlignCenter)
        self._horz_scroll_bar = self.horizontalScrollBar()
        self._vert_scroll_bar = self.verticalScrollBar()
        self._clipboard = QApplication.clipboard()
        self._last_move_pos = None
        self._lines = []

        self._init_actions()

    def _init_actions(self):

        self._context_menu = QMenu(self)

        self._context_menu.addSection("Mouse Mode")
        mode_action_group = QActionGroup(self)
        self._move_mode_action = self._context_menu.addAction("Move")
        self._move_mode_action.setCheckable(True)
        self._move_mode_action.setChecked(True)
        mode_action_group.addAction(self._move_mode_action)
        self._paint_mode_action = self._context_menu.addAction("Paint")
        self._paint_mode_action.setCheckable(True)
        mode_action_group.addAction(self._paint_mode_action)
        mode_action_group.triggered.connect(self._on_mouse_mode_action_checked)
        self._on_mouse_mode_action_checked(mode_action_group.checkedAction())

        self._context_menu.addSection("Pen Width")
        pen_width_action_group = QActionGroup(self)
        for width in (2, 3, 5, 7, 10, 14, 20):
            action = self._context_menu.addAction(str(width) + " px")
            action.setData(width)
            action.setCheckable(True)
            pen_width_action_group.addAction(action)
            if width == 5:
                action.setChecked(True)
        pen_width_action_group.triggered.connect(self._on_pen_width_action_checked)

        self._context_menu.addSeparator()
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence(QKeySequence.Copy))
        copy_action.triggered.connect(self._copy)
        self._context_menu.addAction(copy_action)
        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence(QKeySequence.Paste))
        paste_action.triggered.connect(self._paste)
        self._context_menu.addAction(paste_action)
        reset_scale_action = self._context_menu.addAction("Actual size")
        reset_scale_action.triggered.connect(self._reset_scale)
        clear_action = self._context_menu.addAction("Clear")
        clear_action.triggered.connect(self._image_widget.clear)

        paste_shortcut = QShortcut(paste_action.shortcut(), self)
        paste_shortcut.activated.connect(paste_action.trigger)
        copy_shortcut = QShortcut(copy_action.shortcut(), self)
        copy_shortcut.activated.connect(copy_action.trigger)

    def _on_mouse_mode_action_checked(self, action: QAction):
        self._image_widget.set_paint_enabled(action == self._paint_mode_action)

    def _on_pen_width_action_checked(self, action: QAction) -> None:
        selected_pen_width = int(action.data())
        self._image_widget.set_pen_width(selected_pen_width)

    def _paste(self) -> None:

        print("paste")
        mime_data = self._clipboard.mimeData()
        if mime_data.hasImage():
            image = self._clipboard.image()
            if not image.isNull():
                self._image_widget.set_image(image)
            else:
                print("Image is null")
        else:
            print("Clipboard has no image")

    def _copy(self) -> None:
        print("copy")
        if self._image_widget.has_image():
            self._clipboard.setImage(self._image_widget.get_complex_image())

    def _reset_scale(self):
        self._image_widget.set_scale_factor(1.0)

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

    def _handle_mouse_press_event(self, event: QMouseEvent) -> None:
        if (self._image_widget.has_image() and
                (event.button() == Qt.LeftButton) and (event.buttons() == Qt.LeftButton)):
            self._last_move_pos = event.pos()
        elif self._is_moving():
            self._last_move_pos = None

    def _handle_mouse_release_event(self, event: QMouseEvent) -> None:
        if self._is_moving():
            self._last_move_pos = None

    def _handle_mouse_move_event(self, event: QMouseEvent) -> None:
        if not self._image_widget.has_image():
            return
        if not self._is_moving():
            return
        offset = event.pos() - self._last_move_pos
        self._horz_scroll_bar.setValue(self._horz_scroll_bar.value() - offset.x())
        self._vert_scroll_bar.setValue(self._vert_scroll_bar.value() - offset.y())
        self._last_move_pos = event.pos()

    def _handle_wheel_event(self, event: QWheelEvent) -> None:

        if not self._image_widget.has_image():
            return

        angle_delta_y = event.angleDelta().y()

        if angle_delta_y == 0:
            return

        scale_factor_factor = 1.1
        if angle_delta_y < 0:
            scale_factor_factor = 1.0 / scale_factor_factor
        old_center = self._image_widget.mapFromParent(self.viewport().rect().center())
        self._image_widget.set_scale_factor(self._image_widget.get_scale_factor() * scale_factor_factor)

        new_center = old_center * scale_factor_factor
        offset = new_center - old_center
        self._horz_scroll_bar.setValue(self._horz_scroll_bar.value() + offset.x())
        self._vert_scroll_bar.setValue(self._vert_scroll_bar.value() + offset.y())

    def _handle_context_menu_event(self, event: QContextMenuEvent) -> None:
        self._context_menu.exec_(event.globalPos())
