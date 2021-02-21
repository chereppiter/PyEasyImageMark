import sys
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow

if __name__ == '__main__':

    app = QApplication(sys.argv[:])
    app.setApplicationName("PyEasyImageMark")
    main_widget = MainWindow()
    main_widget.resize(1200, 800)
    main_widget.show()

    sys.exit(app.exec_())
