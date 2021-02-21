from PyQt5.QtWidgets import QMainWindow, QLabel
from EditorWidget import EditorWidget, EditorWidgetMode


class MainWindow(QMainWindow):

    _STATUS_MESSAGE_SHOW_TIMEOUT_MS = 7000

    def __init__(self):
        super().__init__()

        editor_widget = EditorWidget(self)
        self.setCentralWidget(editor_widget)

        status_bar = self.statusBar()
        status_bar.showMessage("Welcome to PyEasyImageMark! Please paste source image to start")

        self._editor_mode_label = QLabel(self)
        self._editor_mode_label.setFixedWidth(100)
        status_bar.addPermanentWidget(self._editor_mode_label)

        self._pen_width_label = QLabel(self)
        self._pen_width_label.setFixedWidth(120)
        status_bar.addPermanentWidget(self._pen_width_label)

        self._image_scale_label = QLabel(self)
        self._image_scale_label.setFixedWidth(100)
        status_bar.addPermanentWidget(self._image_scale_label)

        editor_widget.status_message_request.connect(self._show_status_message)
        editor_widget.mode_changed.connect(self._update_editor_mode_message)
        self._update_editor_mode_message(editor_widget.get_mode())
        editor_widget.pen_width_changed.connect(self._update_pen_width_message)
        self._update_pen_width_message(editor_widget.get_pen_width())
        editor_widget.scale_factor_changed.connect(self._update_scale_message)
        self._update_scale_message(editor_widget.get_scale_factor())

    def _show_status_message(self, message: str) -> None:
        self.statusBar().showMessage(message, MainWindow._STATUS_MESSAGE_SHOW_TIMEOUT_MS)

    def _update_editor_mode_message(self, editor_mode: EditorWidgetMode) -> None:
        self._editor_mode_label.setText("Mode: " + editor_mode.name)

    def _update_pen_width_message(self, pen_width: int) -> None:
        self._pen_width_label.setText("Pen width: " + str(pen_width) + "px")

    def _update_scale_message(self, scale_factor: float):
        self._image_scale_label.setText("Scale: "+ str(round(scale_factor * 100)) + "%")
