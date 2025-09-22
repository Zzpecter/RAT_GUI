import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QPointF

from models.data_model import BoundingBox
from views.main_window import MainWindow
import config


class MainController:
    def __init__(self, view: MainWindow):
        self.view = view
        self._connect_signals()

        # Application state variables from initVars
        self.current_frame_idx = 0
        self.num_frames = 0
        self.frame_dir = ""
        self.project_name = ""
        self.author = ""

        self.main_annotations = []  # This is the bBoxList
        self.secondary_annotations = []  # This is the secBoxList

    def _connect_signals(self):
        """Connect signals from the view to controller slots."""
        # File menu actions
        self.view.actionNewProject.triggered.connect(self.new_project)
        self.view.actionSaveProject.triggered.connect(self.save_annotations)
        # ... other file actions

        # Player controls
        self.view.btnOneFrameFwd.clicked.connect(lambda: self.jump_frames(1))
        self.view.btnOneFrameBwd.clicked.connect(lambda: self.jump_frames(-1))
        self.view.hSliderVideoProgress.sliderMoved.connect(self.slider_moved)

        # Annotation controls
        self.view.btnDelete.clicked.connect(self.delete_annotation)

        # Scene signals
        self.view.scene.new_box_drawn.connect(self.add_new_annotation)

    def new_project(self):
        # All the logic from your original newProject method
        file_name, _ = QFileDialog.getOpenFileName(self.view, "Select Video", "", "MP4 Video (*.mp4)")
        if not file_name:
            return

        # ... create project folders, extract frames with ffmpeg, etc.
        self.project_name = os.path.basename(file_name).split('.')[0]
        self.frame_dir = os.path.join(config.DEFAULT_PROJECTS_DIR, self.project_name, "images")
        self.num_frames = len(os.listdir(self.frame_dir))

        # After setup, load the first frame
        self.current_frame_idx = 0
        self._update_view_for_current_frame()

    def jump_frames(self, num_frames):
        """Jump forward or backward a number of frames."""
        new_idx = self.current_frame_idx + num_frames
        if 0 <= new_idx < self.num_frames:
            self.current_frame_idx = new_idx
            self._update_view_for_current_frame()

    def slider_moved(self, position):
        """Handle the video progress slider being moved."""
        if 0 <= position < self.num_frames:
            self.current_frame_idx = position
            self._update_view_for_current_frame()

    def _update_view_for_current_frame(self):
        """Load the current frame, draw it, and update annotations."""
        frame_path = os.path.join(self.frame_dir, f"{self.current_frame_idx + 1:012d}.jpg")  # Assuming filename format
        if not os.path.exists(frame_path):
            return

        # Load and display image
        cv_frame = cv2.imread(frame_path)
        rgb_frame = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.view.set_frame_image(q_image)

        # Update UI elements
        self.view.update_frame_label(self.current_frame_idx + 1, self.num_frames)
        self.view.hSliderVideoProgress.setValue(self.current_frame_idx)

        # Update annotations
        self._draw_annotations_for_current_frame()
        self._update_table_for_current_frame()

    def add_new_annotation(self, rect):
        """Slot to handle the new_box_drawn signal from the scene."""
        new_box = BoundingBox(
            point1=rect.topLeft(),
            point2=rect.bottomRight(),
            frame_num=self.current_frame_idx + 1
        )
        self.main_annotations.append(new_box)
        self._draw_annotations_for_current_frame()
        self._update_table_for_current_frame()

    def delete_annotation(self):
        # ... logic to delete the selected annotation
        pass

    def _draw_annotations_for_current_frame(self):
        """Clear the scene and draw all boxes for the current frame."""
        self.view.scene.clear_boxes()
        for box in self.main_annotations:
            if box.is_in_frame(self.current_frame_idx + 1):
                self.view.scene.add_box(box.get_qrectf(), box.color)
        # Also draw secondary annotations if loaded

    def _update_table_for_current_frame(self):
        """Filter annotations for the current frame and update the table view."""
        current_anns = [box for box in self.main_annotations if box.is_in_frame(self.current_frame_idx + 1)]
        self.view.update_annotations_table(current_anns)

    # ... all other logic methods: save_annotations, load_project, matchTemplate, getOFFilter, etc.