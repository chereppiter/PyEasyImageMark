import sys
from PyQt5.QtWidgets import QApplication
from MainWidget import MainWidget

if __name__ == '__main__':

    app = QApplication(sys.argv[:])
    app.setApplicationName("PyEasyImageMark")
    main_widget = MainWidget()
    main_widget.resize(1200, 800)
    main_widget.show()

    sys.exit(app.exec_())
