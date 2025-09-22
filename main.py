# my_pyqt_app/main.py

import sys
from PyQt5.QtWidgets import QApplication
from views.main_window import MainWindow
from controllers.main_controller import MainController


def main():
    """Main function to launch the application."""
    app = QApplication(sys.argv)

    # Create the view (GUI)
    view = MainWindow()
    view.show()

    # Create the controller and pass the view to it
    controller = MainController(view=view)

    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()