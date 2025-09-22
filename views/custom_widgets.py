from PyQt5.QtCore import QRectF, QPointF, pyqtSignal, Qt
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsRectItem
from PyQt5.QtGui import QTransform
import numpy as np


class AnnotationScene(QGraphicsScene):
    """A custom QGraphicsScene for drawing and interacting with bounding boxes."""

    # Signals to communicate with the controller
    new_box_drawn = pyqtSignal(QRectF)
    box_selected = pyqtSignal(QGraphicsRectItem)
    auto_box_requested = pyqtSignal(QPointF)
    box_moved = pyqtSignal(QGraphicsRectItem, QPointF)

    def __init__(self, parent=None):
        super().__init__(QRectF(0, 0, 960, 540), parent)
        self.start_point = QPointF()
        self.current_rect_item = None
        self.is_drawing = False
        self.is_moving = False

    def mousePressEvent(self, event):
        self.start_point = event.scenePos()
        self.is_drawing = True

        # Logic to check if an existing item is being moved
        # ...

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            if not self.current_rect_item:
                self.current_rect_item = QGraphicsRectItem()
                self.current_rect_item.setPen(Qt.red)
                self.addItem(self.current_rect_item)

            rect = QRectF(self.start_point, event.scenePos()).normalized()
            self.current_rect_item.setRect(rect)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        end_point = event.scenePos()
        distance = (end_point - self.start_point).manhattanLength()

        if self.current_rect_item and distance > 10:  # User drew a new box
            self.new_box_drawn.emit(self.current_rect_item.rect())
        elif distance <= 10:  # User clicked to create an auto-sized box
            self.auto_box_requested.emit(self.start_point)

        if self.current_rect_item:
            self.removeItem(self.current_rect_item)
            self.current_rect_item = None

        self.is_drawing = False
        super().mouseReleaseEvent(event)

    def clear_boxes(self):
        """Remove all annotation boxes from the scene."""
        for item in self.items():
            if isinstance(item, QGraphicsRectItem):
                self.removeItem(item)

    def add_box(self, rect, color):
        """Add a single box to the scene, called by the controller."""
        box_item = QGraphicsRectItem(rect)
        box_item.setPen(color)
        box_item.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.addItem(box_item)
        return box_item
