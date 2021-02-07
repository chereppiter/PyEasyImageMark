import sys
from PySide6.QtWidgets import QApplication
from MainWidget import MainWidget

if __name__ == '__main__':

    app = QApplication(sys.argv[:])
    main_widget = MainWidget()
    main_widget.resize(800, 500)
    main_widget.show()

    sys.exit(app.exec_())
