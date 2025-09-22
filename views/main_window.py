from PyQt5 import QtCore, QtGui, QtWidgets
from .custom_widgets import AnnotationScene


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        # All the widget creation and layout code from your original setupUi method
        # goes here. For example:
        self.setObjectName("windowRAT")
        self.resize(1420, 740)

        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # Video Player GroupBox
        self.gbVideoPlayer = QtWidgets.QGroupBox("Video Player", self.centralwidget)
        self.gbVideoPlayer.setGeometry(QtCore.QRect(10, 10, 990, 670))

        self.gvFrameDisplay = QtWidgets.QGraphicsView(self.gbVideoPlayer)
        self.gvFrameDisplay.setGeometry(QtCore.QRect(10, 20, 960, 540))

        # Use our custom scene
        self.scene = AnnotationScene()
        self.pixmap_item = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self.gvFrameDisplay.setScene(self.scene)

        self.hSliderVideoProgress = QtWidgets.QSlider(QtCore.Qt.Horizontal, self.gbVideoPlayer)
        self.hSliderVideoProgress.setGeometry(QtCore.QRect(10, 575, 960, 22))

        self.btnOneFrameFwd = QtWidgets.QPushButton(">", self.gbVideoPlayer)
        self.btnOneFrameFwd.setGeometry(QtCore.QRect(560, 620, 93, 28))

        # ... and so on for every other widget.

        # Annotations GroupBox
        self.gbAnnotations = QtWidgets.QGroupBox("Annotations", self.centralwidget)
        self.gbAnnotations.setGeometry(QtCore.QRect(1000, 10, 400, 660))

        self.tblAnnotations = QtWidgets.QTableWidget(self.gbAnnotations)
        self.tblAnnotations.setGeometry(QtCore.QRect(20, 110, 350, 450))
        self.tblAnnotations.setColumnCount(3)
        self.tblAnnotations.setHorizontalHeaderLabels(['Frame', 'Class', 'Location'])

        self.btnDelete = QtWidgets.QPushButton("Delete", self.gbAnnotations)
        self.btnDelete.setGeometry(QtCore.QRect(140, 600, 93, 28))

        # Menu Bar
        self.menubar = self.menuBar()
        self.menuFile = self.menubar.addMenu('&File')
        self.menuTools = self.menubar.addMenu('&Tools')

        self.actionNewProject = QtWidgets.QAction('&New Project', self)
        self.actionSaveProject = QtWidgets.QAction('&Save Project', self)
        # ... etc. for all menu actions

        self.menuFile.addAction(self.actionNewProject)
        self.menuFile.addAction(self.actionSaveProject)

    def set_frame_image(self, q_image):
        """Updates the pixmap in the scene with a new frame image."""
        pixmap = QtGui.QPixmap.fromImage(q_image)
        self.pixmap_item.setPixmap(pixmap)

    def update_frame_label(self, current_frame, total_frames):
        """Updates the frame counter label."""
        self.lblFrameNumber.setText(f"Frame: {current_frame}/{total_frames}")

    def update_annotations_table(self, annotations_for_current_frame):
        """Clears and repopulates the annotations table."""
        self.tblAnnotations.setRowCount(0)
        for i, ann in enumerate(annotations_for_current_frame):
            self.tblAnnotations.insertRow(i)
            self.tblAnnotations.setItem(i, 0, QtWidgets.QTableWidgetItem(str(ann.frame)))
            self.tblAnnotations.setItem(i, 1, QtWidgets.QTableWidgetItem(ann.class_name))
            # ... add other columns

    # Add more simple methods like these to update UI elements