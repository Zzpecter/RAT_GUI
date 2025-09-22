import numpy as np
from PyQt5.QtCore import QPointF, QRectF, Qt
from shapely.geometry import Polygon


class BoundingBox:
    """Represents a single bounding box annotation."""

    def __init__(self, point1=None, point2=None, frame_num=0, color=Qt.red, class_name='person'):
        self.point1 = point1
        self.point2 = point2
        self.frame = frame_num
        self.color = color
        self.class_name = class_name
        self.rect_item = None  # To hold the QGraphicsRectItem from the view

        # Calculate width, height, and center point
        self.w = np.abs(self.point2.x() - self.point1.x())
        self.h = np.abs(self.point2.y() - self.point1.y())
        self.center_point = self.get_center_point()

    def get_center_point(self):
        """Calculates the center point of the bounding box."""
        cx = (self.point1.x() + self.point2.x()) / 2
        cy = (self.point1.y() + self.point2.y()) / 2
        return QPointF(cx, cy)

    def get_qrectf(self):
        """Returns the bounding box as a QRectF object."""
        return QRectF(self.point1, self.point2).normalized()

    def get_label_notation(self, frame_width, frame_height):
        """Generates the annotation string for YOLO-style label files."""
        norm_center_x = self.center_point.x() / frame_width
        norm_center_y = self.center_point.y() / frame_height
        norm_w = self.w / frame_width
        norm_h = self.h / frame_height
        return f'0 {norm_center_x:.6f} {norm_center_y:.6f} {norm_w:.6f} {norm_h:.6f}\n'

    def is_in_frame(self, frame_idx):
        """Checks if the bounding box belongs to the given frame index."""
        return self.frame == frame_idx

    def calc_iou(self, other_box):
        """Calculates the Intersection over Union (IoU) with another BoundingBox."""
        # Using shapely for simplicity and accuracy
        r1 = Polygon([(self.point1.x(), self.point1.y()), (self.point2.x(), self.point1.y()),
                      (self.point2.x(), self.point2.y()), (self.point1.x(), self.point2.y())])
        r2 = Polygon([(other_box.point1.x(), other_box.point1.y()), (other_box.point2.x(), other_box.point1.y()),
                      (other_box.point2.x(), other_box.point2.y()), (other_box.point1.x(), other_box.point2.y())])

        intersection_area = r1.intersection(r2).area
        union_area = r1.union(r2).area

        return intersection_area / union_area if union_area > 0 else 0

    # ... other helper methods from MyBBox like getLoc, getCoordList, etc.