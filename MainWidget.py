from PyQt5.QtWidgets import QWidget, QVBoxLayout
from EditorWidget import EditorWidget


class MainWidget(QWidget):

    def __init__(self):
        super().__init__()

        editor = EditorWidget(self)
        content_layout = QVBoxLayout(self)
        content_layout.addWidget(editor)
        self.setLayout(content_layout)
