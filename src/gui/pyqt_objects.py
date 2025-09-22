import random
import numpy as np
import sys
import cv2
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from utils.constants import DEFAULT_BBOX_POINT_DICT
# ={
#     'ctr': None,
#     'tl':None,
#     'br':None,
#
# },


class PyqtBBox:
    def __init__(self, points=DEFAULT_BBOX_POINT_DICT, color=Qt.red,
                 frame_index=0, class_name='person', source='Manual'):
        if points['ctr'] is not None and points['w'] is not None and points['h'] is not None:
            tlx = points['ctr'] - points['w']/2
            tly = points['ctr'] - points['h']/2
            w = points['w']
            h = points['h']
        elif points['tl'] is not None and points['br'] is not None:
            tlx = points['tl'][0]
            tly = points['tl'][1]
            w = abs(points['tl'][0] - points['br'][0])
            h = abs(points['tl'][1] - points['br'][1])
        elif points['tl'] is not None and points['w'] is not None and points['h'] is not None:
            tlx = points['tl'][0]
            tly = points['tl'][1]
            w = points['w']
            h = points['h']
        elif points['br'] is not None and points['w'] is not None and points['h'] is not None:
            tlx = points['br'][0] - points['w']
            tly = points['br'][1] - points['h']
            w = points['w']
            h = points['h']
        else:
            raise ValueError

        self.qt_rect = QtCore.QRectF(tlx, tly, w, h)
        self.frame_index = frame_index
        self.class_name = class_name
        self.source = source
        self.color = color


class MainWindowGS(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super(MainWindowGS, self).__init__(QtCore.QRectF(0, 0, 960, 540), parent)
        self.tempRect = None
        self.pointPressed = QtCore.QPointF()
        self.pointReleased = QtCore.QPointF()
        self.dist = 0

        self.itemSelected = False
        self.movingSelected = False
        self.selectedIdx = 0

        self.startPoint = QtCore.QPointF()
        self.fillerP = QtCore.QPointF(0.5, 0.5)
        self.newRect = False
        self.rectList = []
        self.iPointMov = QtCore.QPointF()
        self.defaultSize = [40, 80]
        self.grabbedIdx = 0

    def mousePressEvent(self, event):
        player.btnDelete.setEnabled(False)
        self.dist = 0
        self.pointPressed = event.scenePos()
        print('pointPressed: {}'.format(self.pointPressed))


        if self.itemSelected and self.itemAt(event.scenePos(), QtGui.QTransform()).sceneBoundingRect().getCoords() == \
                player.bBoxList[self.selectedIdx].rectObject.sceneBoundingRect().getCoords():
            # if clicking on selected object, dont create new rect
            print('self.movingSelected = True')
            self.movingSelected = True
            self.tempRect = self.itemAt(event.scenePos(), QtGui.QTransform())


        elif self.itemSelected:
            self.itemSelected = False
            player.bBoxList[self.selectedIdx].col = Qt.red
            player.bBoxList[self.selectedIdx].rectObject.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.selectedIdx = 0

        if not self.movingSelected:
            self.tempRect = QGraphicsRectItem()
            self.tempRect.setPen(Qt.red)
            self.tempRect.setFlag(QGraphicsItem.ItemIsMovable, False)
            self.tempRect.setRect(QRectF(self.pointPressed, self.pointPressed))
            self.addItem(self.tempRect)

        super(MyGraphicsScene, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.dist = (event.scenePos() - self.pointPressed).manhattanLength()
        print('currentDist: {}'.format(self.dist))

        if not self.movingSelected and self.dist > 30:  # draw a new rect
            self.tempRect.setRect(QRectF(self.pointPressed, event.scenePos()).normalized())

        elif self.movingSelected:  # draw the moving rect
            super(MyGraphicsScene, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.pointReleased = event.scenePos()
        print('pointReleased: {}'.format(self.pointReleased))
        # clip pointReleased
        self.pointReleased.setX(np.clip(self.pointReleased.x(), 0, 960))
        self.pointReleased.setY(np.clip(self.pointReleased.y(), 0, 540))
        print('Clipped pointReleased: {}'.format(self.pointReleased))

        if self.dist > 30 and not self.movingSelected:
            self.itemSelected = False
            self.movingSelected = False
            # orders the points
            p1 = QPointF(np.minimum(self.pointPressed.x(), self.pointReleased.x()),
                         np.minimum(self.pointPressed.y(), self.pointReleased.y()))
            p2 = QPointF(np.maximum(self.pointPressed.x(), self.pointReleased.x()),
                         np.maximum(self.pointPressed.y(), self.pointReleased.y()))
            self.tempRect.setRect(QRectF(p1, p2).normalized())

            # creates new BBox
            player.bBoxList.append(
                MyBBox(point1=p1, point2=p2, fr=player.currentFrameIdx + 1, rectObject=self.tempRect))
            annCountIdx = int(np.ceil(player.currentFrameIdx / player.numFrames * 95))
            player.annCount[annCountIdx] += 1
            player.drawAnnCount()

            if player.useTemplateMatching:
                player.matchTemplate([p1.x(), p1.y(), p2.x(), p2.y()])

            self.rectList.append(self.tempRect)
            self.removeItem(self.tempRect)
            self.addItem(player.bBoxList[len(player.bBoxList) - 1].rectObject)

        elif self.dist < 30 and self.itemAt(self.pointReleased,
                                            QtGui.QTransform()) is player.pixmap and not self.movingSelected:  # no rects on this space
            self.itemSelected = False
            self.movingSelected = False
            # create autobox
            player.bBoxList.append(
                MyBBox(point1=self.pointPressed, point2=self.pointPressed, fr=player.currentFrameIdx + 1))

            player.bBoxList[len(player.bBoxList) - 1].w = player.minBoxSize.x()
            player.bBoxList[len(player.bBoxList) - 1].h = player.minBoxSize.y()
            player.bBoxList[len(player.bBoxList) - 1].getPointsFromCenter()

            # clip autobox
            player.bBoxList[len(player.bBoxList) - 1].point1.setX(
                np.clip(player.bBoxList[len(player.bBoxList) - 1].point1.x(), 0, 960))
            player.bBoxList[len(player.bBoxList) - 1].point2.setX(
                np.clip(player.bBoxList[len(player.bBoxList) - 1].point2.x(), 0, 960))

            player.bBoxList[len(player.bBoxList) - 1].point1.setY(
                np.clip(player.bBoxList[len(player.bBoxList) - 1].point1.y(), 0, 540))
            player.bBoxList[len(player.bBoxList) - 1].point2.setY(
                np.clip(player.bBoxList[len(player.bBoxList) - 1].point2.y(), 0, 540))

            annCountIdx = int(np.ceil(player.currentFrameIdx / player.numFrames * 95))
            player.annCount[annCountIdx] += 1
            player.drawAnnCount()

            self.tempRect.setRect((player.bBoxList[len(player.bBoxList) - 1].getQRectF()).normalized())
            player.bBoxList[len(player.bBoxList) - 1].rectObject = self.tempRect

            if player.useTemplateMatching:
                player.matchTemplate([p1.x(), p1.y(), p2.x(), p2.y()])

            self.rectList.append(self.tempRect)
            self.removeItem(self.tempRect)
            self.addItem(player.bBoxList[len(player.bBoxList) - 1].rectObject)

        elif self.dist < 30 and self.itemAt(self.pointReleased,
                                            QtGui.QTransform()) is not player.pixmap and not self.movingSelected:  # there is a rect on this space

            player.btnDelete.setEnabled(True)
            c = self.itemAt(event.scenePos(), QtGui.QTransform()).sceneBoundingRect().getCoords()

            print('Selected rect Coords: {}'.format(c))
            p1 = QPointF(c[0], c[1]) + self.fillerP
            p2 = QPointF(c[2], c[3]) - self.fillerP
            print('p1: {} p2: {}'.format(p1, p2))

            self.itemSelected = True
            self.movingSelected = False
            self.selectedIdx = 0

            for bb in player.bBoxList:
                bb.col = Qt.red
            for bb in player.bBoxList:
                if bb.checkFr(player.currentFrameIdx + 1):
                    if bb.point1 == p1 and bb.point2 == p2:
                        bb.col = Qt.green
                        bb.rectObject = self.itemAt(event.scenePos(), QtGui.QTransform())
                        bb.rectObject.setFlag(QGraphicsItem.ItemIsMovable, True)
                        break
                self.selectedIdx += 1
            player.selectedBoxIdx = self.selectedIdx

        elif self.movingSelected:

            print('self.tempRect: {}'.format(self.tempRect.sceneBoundingRect().getCoords()))
            player.bBoxList[self.selectedIdx].rectObject = self.tempRect

            c = player.bBoxList[self.selectedIdx].rectObject.sceneBoundingRect().getCoords()
            print('Selected rect Coords: {}'.format(c))
            p1 = QPointF(c[0], c[1]) + self.fillerP
            p2 = QPointF(c[2], c[3]) - self.fillerP
            print('p1: {} p2: {}'.format(p1, p2))
            self.removeItem(self.tempRect)
            p1.setX(np.clip(p1.x(), 0, 960))
            p2.setX(np.clip(p2.x(), 0, 960))
            p1.setY(np.clip(p1.y(), 0, 540))
            p2.setY(np.clip(p2.y(), 0, 540))

            player.bBoxList[self.selectedIdx].point1 = p1
            player.bBoxList[self.selectedIdx].point2 = p2
            player.bBoxList[self.selectedIdx].getCtrPoint()

            self.movingSelected = False
            self.itemSelected = False

        self.delCurrentRects()
        self.drawCurrentRects()

        super(MyGraphicsScene, self).mouseReleaseEvent(event)

    def drawCurrentRects(self):
        for bb in player.bBoxList:
            if bb.checkFr(player.currentFrameIdx + 1):
                self.tempRect = QGraphicsRectItem()
                self.tempRect.setPen(bb.col)
                self.tempRect.setFlag(QGraphicsItem.ItemIsMovable, True)
                self.addItem(self.tempRect)
                self.tempRect.setRect(bb.getQRectF())
                self.rectList.append(self.tempRect)

        for bb in player.secBoxList:
            if bb.checkFr(player.currentFrameIdx + 1):
                self.tempRect = QGraphicsRectItem()
                self.tempRect.setPen(bb.col)
                self.tempRect.setFlag(QGraphicsItem.ItemIsMovable, False)
                self.addItem(self.tempRect)
                self.tempRect.setRect(bb.getQRectF())
                self.rectList.append(self.tempRect)

    def delCurrentRects(self):
        for item in self.rectList:
            self.removeItem(item)
        self.rectList = []
