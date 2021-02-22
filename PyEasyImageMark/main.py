import sys
from PyQt5.QtWidgets import QApplication
from PyEasyImageMark.MainWindow import MainWindow


def run():
    app = QApplication(sys.argv[:])
    app.setApplicationName("PyEasyImageMark")
    main_widget = MainWindow()
    main_widget.resize(1200, 800)
    main_widget.show()

    sys.exit(app.exec_())
