from PyQt5 import QtCore, QtGui, QtWidgets
import sys


def main():
    app = QtWidgets.QApplication(sys.argv)

    view = MyDialog()
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
