import sys
import numpy as np
from PyQt5.QtWidgets import QApplication
from .mainwindow import MainWindow


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        prog='gravity')

    args = parser.parse_args()
    app = QApplication([])
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
