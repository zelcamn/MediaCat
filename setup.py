import sys

from PyQt5.QtWidgets import QApplication
from mediacat.pyFiles.main import main


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = main()
    ex.show()
    sys.exit(app.exec())
