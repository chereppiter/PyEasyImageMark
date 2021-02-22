from PyQt5.QtWidgets import (QWidget, QScrollArea, QMenu, QApplication,
                             QAction, QShortcut, QActionGroup)
from PyQt5.QtGui import (QKeySequence, QMouseEvent, QWheelEvent, QContextMenuEvent,
                         QCursor, QPixmap, QImage, QPainter)
from PyQt5.QtCore import QEvent, Qt, QRect, pyqtSignal
from PyEasyImageMark.ImageWidget import ImageWidget
from enum import IntEnum, unique


@unique
class EditorWidgetMode(IntEnum):
    Move = 1
    Paint = 2


class EditorWidget(QScrollArea):

    status_message_request = pyqtSignal(str)
    mode_changed = pyqtSignal(EditorWidgetMode)
    pen_width_changed = pyqtSignal(int)
    scale_factor_changed = pyqtSignal(float)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.__image_widget = ImageWidget(self)
        self.setWidget(self.__image_widget)
        self.setAlignment(Qt.AlignCenter)
        self.__horz_scroll_bar = self.horizontalScrollBar()
        self.__vert_scroll_bar = self.verticalScrollBar()
        self.__clipboard = QApplication.clipboard()
        self.__last_move_pos = None
        self.__lines = []

        self.__init_actions()

    def __init_actions(self):

        self.__context_menu = QMenu(self)

        self.__context_menu.addSection("Mouse Mode")
        mode_action_group = QActionGroup(self)
        self.__move_mode_action = self.__context_menu.addAction("Move")
        self.__move_mode_action.setCheckable(True)
        self.__move_mode_action.setChecked(True)
        mode_action_group.addAction(self.__move_mode_action)
        self.__paint_mode_action = self.__context_menu.addAction("Paint")
        self.__paint_mode_action.setCheckable(True)
        mode_action_group.addAction(self.__paint_mode_action)
        mode_action_group.triggered.connect(self.__on_mouse_mode_action_checked)
        self.__on_mouse_mode_action_checked(mode_action_group.checkedAction())

        copy_key_sequence = QKeySequence(QKeySequence.Copy)
        paste_key_sequence = QKeySequence(QKeySequence.Paste)
        undo_key_sequence = QKeySequence(QKeySequence.Undo)

        self.__context_menu.addSection("Pen Width")
        pen_width_action_group = QActionGroup(self)
        for width in (3, 5, 7, 10, 14, 20):
            action = self.__context_menu.addAction(str(width) + " px")
            action.setData(width)
            action.setCheckable(True)
            pen_width_action_group.addAction(action)
            if width == 5:
                action.setChecked(True)
        pen_width_action_group.triggered.connect(self.__on_pen_width_action_checked)
        self.__on_pen_width_action_checked(pen_width_action_group.checkedAction())

        self.__context_menu.addSeparator()
        copy_action = self.__context_menu.addAction("Copy")
        copy_action.setShortcut(copy_key_sequence)
        copy_action.setShortcutVisibleInContextMenu(True)
        copy_action.triggered.connect(self.__copy)
        paste_action = self.__context_menu.addAction("Paste")
        paste_action.setShortcut(paste_key_sequence)
        paste_action.setShortcutVisibleInContextMenu(True)
        paste_action.triggered.connect(self.__paste)
        reset_scale_action = self.__context_menu.addAction("Actual size")
        reset_scale_action.triggered.connect(self.__reset_scale)
        undo_action = self.__context_menu.addAction("Undo")
        undo_action.setShortcut(undo_key_sequence)
        undo_action.setShortcutVisibleInContextMenu(True)
        undo_action.triggered.connect(self.__image_widget.remove_last_line)
        clear_action = self.__context_menu.addAction("Clear")
        clear_action.triggered.connect(self.__image_widget.clear)

        paste_shortcut = QShortcut(paste_key_sequence, self)
        paste_shortcut.activated.connect(paste_action.trigger)
        copy_shortcut = QShortcut(copy_key_sequence, self)
        copy_shortcut.activated.connect(copy_action.trigger)
        undo_shortcut = QShortcut(undo_key_sequence, self)
        undo_shortcut.activated.connect(undo_action.trigger)

    def get_mode(self) -> EditorWidgetMode:
        if self.__image_widget.is_paint_enabled():
            return EditorWidgetMode.Paint
        return EditorWidgetMode.Move

    def get_pen_width(self) -> int:
        return self.__image_widget.get_pen_width()

    def get_scale_factor(self) -> float:
        return self.__image_widget.get_scale_factor()

    def __on_mouse_mode_action_checked(self, action: QAction) -> None:
        paint_mode_on = (action == self.__paint_mode_action)
        self.__image_widget.set_paint_enabled(paint_mode_on)
        if paint_mode_on:
            self.__image_widget.setCursor(self.__get_pen_cursor())
        else:
            self.__image_widget.setCursor(Qt.SizeAllCursor)
        self.mode_changed.emit(self.get_mode())

    def __on_pen_width_action_checked(self, action: QAction) -> None:
        selected_pen_width = int(action.data())
        self.__image_widget.set_pen_width(selected_pen_width)
        if self.__image_widget.is_paint_enabled():
            self.__image_widget.setCursor(self.__get_pen_cursor())
        self.pen_width_changed.emit(selected_pen_width)

    def __get_pen_cursor(self) -> QCursor:
        image = QImage(32, 32, QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.transparent)
        pen_diam = self.__image_widget.get_pen_width()
        pen_rect = QRect(0, 0, pen_diam, pen_diam)
        pen_rect.moveCenter(image.rect().center())
        painter = QPainter(image)
        painter.drawEllipse(pen_rect)
        painter.end()
        return QCursor(QPixmap.fromImage(image))

    def __paste(self) -> None:

        print("paste")
        mime_data = self.__clipboard.mimeData()
        if mime_data.hasImage():
            image = self.__clipboard.image()
            if not image.isNull():
                self.__image_widget.set_image(image)
                self.status_message_request.emit("Image pasted from clipboard")
            else:
                print("Image is null")
                self.status_message_request.emit("Clipboard has no image")
        else:
            print("Clipboard has no image")
            self.status_message_request.emit("Clipboard has no image")

    def __copy(self) -> None:
        print("copy")
        if self.__image_widget.has_image():
            self.__clipboard.setImage(self.__image_widget.get_complex_image())
            self.status_message_request.emit("Image is copied to clipboard")
        else:
            self.status_message_request.emit("No image to copy")

    def __reset_scale(self):
        self.__set_scale_factor(1.0)

    def viewportEvent(self, event: QEvent) -> bool:

        if event.type() == QEvent.MouseButtonPress:
            self.__handle_mouse_press_event(event)
        elif event.type() == QEvent.MouseButtonRelease:
            self.__handle_mouse_release_event(event)
        elif event.type() == QEvent.MouseMove:
            self.__handle_mouse_move_event(event)
        elif event.type() == QEvent.Wheel:
            self.__handle_wheel_event(event)
        elif event.type() == QEvent.ContextMenu:
            self.__handle_context_menu_event(event)
        else:
            return False
        return True

    def __is_moving(self) -> bool:
        return self.__last_move_pos is not None

    def __handle_mouse_press_event(self, event: QMouseEvent) -> None:
        if self.__image_widget.has_image():
            if ((event.button() == event.buttons() == Qt.LeftButton) or
                    (event.button() == event.buttons() == Qt.MiddleButton)):
                self.__last_move_pos = event.pos()
                return
        self.__last_move_pos = None

    def __handle_mouse_release_event(self, event: QMouseEvent) -> None:
        if self.__is_moving():
            self.__last_move_pos = None

    def __handle_mouse_move_event(self, event: QMouseEvent) -> None:
        if not self.__image_widget.has_image():
            return
        if not self.__is_moving():
            return
        offset = event.pos() - self.__last_move_pos
        self.__horz_scroll_bar.setValue(self.__horz_scroll_bar.value() - offset.x())
        self.__vert_scroll_bar.setValue(self.__vert_scroll_bar.value() - offset.y())
        self.__last_move_pos = event.pos()

    def __handle_wheel_event(self, event: QWheelEvent) -> None:

        if not self.__image_widget.has_image():
            return

        angle_delta_y = event.angleDelta().y()

        if angle_delta_y == 0:
            return

        scale_factor_factor = 1.1
        if angle_delta_y < 0:
            scale_factor_factor = 1.0 / scale_factor_factor
        old_center = self.__image_widget.mapFromParent(self.viewport().rect().center())
        self.__set_scale_factor(self.__image_widget.get_scale_factor() * scale_factor_factor)

        new_center = old_center * scale_factor_factor
        offset = new_center - old_center
        self.__horz_scroll_bar.setValue(self.__horz_scroll_bar.value() + offset.x())
        self.__vert_scroll_bar.setValue(self.__vert_scroll_bar.value() + offset.y())

    def __handle_context_menu_event(self, event: QContextMenuEvent) -> None:
        self.__context_menu.exec_(event.globalPos())

    def __set_scale_factor(self, scale_factor: float) -> None:
        self.__image_widget.set_scale_factor(scale_factor)
        self.scale_factor_changed.emit(scale_factor)
