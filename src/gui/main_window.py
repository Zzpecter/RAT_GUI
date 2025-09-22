from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QSizePolicy, QGroupBox

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__()

        self.setupUi()
        self.initVars()
        self.show()

    def initVars(self):

        self.currentFrameIdx = 0
        self.frameWidth = 960
        self.frameHeight = 540
        self.frameChannels = 3
        self.bytesPerLine = self.frameWidth * self.frameChannels

        # Vars specific to partial frame loading
        self.numFrames = 0  # total number of frames

        self.anchorFrame = 0  # The loadingSpan surrounding frames from this one are loaded
        self.loadingSpan = 10  # loads +-n frames from the anchorFrame
        self.localIndex = 0  # idx between -self.loadingSpan to +self.loadingSpan
        self.lowerF, self.upperF = 0, self.loadingSpan  # frame nums between which frames are loaded

        self.totalTimeSec = 0
        self.totalTimeMin = 0
        self.currentTimeSec = 0
        self.currentTimeMin = 0
        self.timeString = ''
        self.author = ''

        self.useTemplateMatching = False
        self.tmFrameSpan = 7
        self.tmThresh = 0.98

        self.strippedName = ''
        self.frameDir = ''
        self.selectedBoxIdx = 0
        self.bBoxList = []  # the mother list of all boxes

        self.tableAnnotationIndexer = []
        self.selectedTableIdx = 0
        self.minBoxSize = QPointF(20, 40)
        self.demoBoxShowing = False
        self.demoBoxP1 = QPointF(50, 50)
        self.demoBoxP2 = QPointF()
        self.copyBoxList = []
        self.initialIdx = -1  # for copying

        self.secBoxList = []
        self.playerState = 'empty'

        self.generateOFFilter = True
        self.OFFilter = np.zeros((self.frameWidth, self.frameHeight))

        self.annCount = np.zeros([96])  # 960pixels/10 = each box to color 10*10pix
        self.newBoxes = []

    def setupUi(self):
        self.setWindowTitle("Video Annotation Tool")
        self.setObjectName("windowRAT")
        self.resize(1420, 740)

        size_policy = QSizePolicy(QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        self.setSizePolicy(size_policy)

        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("centralwidget")
        self.setWindowIcon(QtGui.QIcon('ratIcon.png'))

        self.gbVideoPlayer = QGroupBox(self.central_widget)
        self.gbVideoPlayer.setGeometry(QtCore.QRect(10, 10, 990, 670))
        self.gbVideoPlayer.setMinimumSize(QtCore.QSize(980, 660))
        self.gbVideoPlayer.setMaximumSize(QtCore.QSize(9b80, 660))
        self.gbVideoPlayer.setObjectName("gbVideoPlayer")

        self.gbAnnotations = QGroupBox(self.central_widget)
        self.gbAnnotations.setGeometry(QtCore.QRect(1000, 10, 1400, 660))
        self.gbAnnotations.setMinimumSize(QtCore.QSize(400, 650))
        self.gbAnnotations.setMaximumSize(QtCore.QSize(400, 650))
        self.gbAnnotations.setObjectName("gbAnnotations")

        self.btnOneFrameFwd = QtWidgets.QPushButton(self.gbVideoPlayer)
        self.btnOneFrameFwd.setGeometry(QtCore.QRect(560, 620, 93, 28))
        self.btnOneFrameFwd.setObjectName("btnOneFrameFwd")
        self.btnOneFrameFwd.setEnabled(False)
        self.btnOneFrameFwd.clicked.connect(self.oneFrameFwd)

        self.btnOneFrameBwd = QtWidgets.QPushButton(self.gbVideoPlayer)
        self.btnOneFrameBwd.setGeometry(QtCore.QRect(290, 620, 93, 28))
        self.btnOneFrameBwd.setObjectName("btnOneFrameBwd")
        self.btnOneFrameBwd.setEnabled(False)
        self.btnOneFrameBwd.clicked.connect(self.oneFrameBwd)

        self.btnFiveFramesFwd = QtWidgets.QPushButton(self.gbVideoPlayer)
        self.btnFiveFramesFwd.setGeometry(QtCore.QRect(650, 620, 93, 28))
        self.btnFiveFramesFwd.setObjectName("btnFiveFramesFwd")
        self.btnFiveFramesFwd.setEnabled(False)
        self.btnFiveFramesFwd.clicked.connect(self.fiveFramesFwd)

        self.btnFiveFramesBwd = QtWidgets.QPushButton(self.gbVideoPlayer)
        self.btnFiveFramesBwd.setGeometry(QtCore.QRect(200, 620, 93, 28))
        self.btnFiveFramesBwd.setObjectName("btnFiveFramesBwd")
        self.btnFiveFramesBwd.setEnabled(False)
        self.btnFiveFramesBwd.clicked.connect(self.fiveFramesBwd)

        self.hSliderVideoProgress = QtWidgets.QSlider(self.gbVideoPlayer)
        self.hSliderVideoProgress.setGeometry(QtCore.QRect(10, 575, 960, 22))
        self.hSliderVideoProgress.setOrientation(QtCore.Qt.Horizontal)
        self.hSliderVideoProgress.setObjectName("hSliderVideoProgress")
        self.hSliderVideoProgress.setMinimum(0)
        self.hSliderVideoProgress.setTickInterval(1)
        self.hSliderVideoProgress.setSingleStep(1)
        self.hSliderVideoProgress.sliderMoved.connect(self.sliderMoved)

        self.gvFrameDisplay = QtWidgets.QGraphicsView(self.gbVideoPlayer)
        self.gvFrameDisplay.setGeometry(QtCore.QRect(10, 20, 960, 540))
        self.gvFrameDisplay.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.gvFrameDisplay.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.gvFrameDisplay.setObjectName("gvFrameDisplay")

        self.scene = MyGraphicsScene()
        self.pixmap = QGraphicsPixmapItem()
        self.pixmap.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.scene.addItem(self.pixmap)
        self.gvFrameDisplay.setScene(self.scene)
        self.gvFrameDisplay.setEnabled(False)

        # scene = QtWidgets.QGraphicsScene(self)
        # view = QtWidgets.QGraphicsView(scene)

        self.tagScene = QGraphicsScene(self)

        self.gvTagOverview = QtWidgets.QGraphicsView(self.gbVideoPlayer)
        self.gvTagOverview.setScene(self.tagScene)
        self.gvTagOverview.setGeometry(QtCore.QRect(10, 605, 960, 10))
        self.gvTagOverview.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.gvTagOverview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.gvTagOverview.setObjectName("gvTagOverview")

        self.lblFrameNumber = QtWidgets.QLabel(self.gbVideoPlayer)
        self.lblFrameNumber.setGeometry(QtCore.QRect(420, 560, 150, 16))
        self.lblFrameNumber.setWordWrap(True)
        self.lblFrameNumber.setObjectName("lblFrameNumber")

        self.cbMainAnn = QtWidgets.QCheckBox(self.gbAnnotations)
        self.cbMainAnn.setGeometry(QtCore.QRect(20, 20, 230, 20))
        self.cbMainAnn.setObjectName("cbMainAnn")
        self.cbMainAnn.setStyleSheet('color: red')
        self.cbMainAnn.setChecked(False)
        self.cbMainAnn.setEnabled(False)

        self.cbSecAnn = QtWidgets.QCheckBox(self.gbAnnotations)
        self.cbSecAnn.setGeometry(QtCore.QRect(20, 35, 230, 20))
        self.cbSecAnn.setObjectName("cbSecAnn")
        self.cbSecAnn.setStyleSheet('color: cyan')
        self.cbSecAnn.setChecked(False)
        self.cbSecAnn.setEnabled(False)

        self.btnPerformance = QtWidgets.QPushButton(self.gbAnnotations)
        self.btnPerformance.setGeometry(QtCore.QRect(280, 25, 100, 30))
        self.btnPerformance.setEnabled(False)
        self.btnPerformance.setObjectName("btnPerformance")
        self.btnPerformance.clicked.connect(self.openPerfWindow)

        self.rbMainAnn = QRadioButton(self.gbAnnotations)
        self.rbMainAnn.setGeometry(QtCore.QRect(20, 60, 180, 20))
        self.rbMainAnn.setObjectName("rbMainAnn")
        self.rbMainAnn.setChecked(True)
        self.rbMainAnn.toggled.connect(self.updateTable)

        self.rbSecAnn = QRadioButton(self.gbAnnotations)
        self.rbSecAnn.setGeometry(QtCore.QRect(200, 60, 180, 20))
        self.rbSecAnn.setObjectName("rbSecAnn")
        self.rbSecAnn.setEnabled(False)
        self.rbSecAnn.toggled.connect(self.updateTable)

        self.lblRecall = QtWidgets.QLabel(self.gbAnnotations)
        self.lblRecall.setGeometry(QtCore.QRect(20, 80, 150, 16))
        self.lblRecall.setWordWrap(True)
        self.lblRecall.setObjectName("lblRecall")
        self.lblRecall.setVisible(False)

        self.lblPrecision = QtWidgets.QLabel(self.gbAnnotations)
        self.lblPrecision.setGeometry(QtCore.QRect(200, 80, 150, 16))
        self.lblPrecision.setWordWrap(True)
        self.lblPrecision.setObjectName("lblPrecision")
        self.lblPrecision.setVisible(False)

        self.tblAnnotations = QTableWidget(self.gbAnnotations)
        self.tblAnnotations.setGeometry(QtCore.QRect(20, 110, 350, 450))
        self.tblAnnotations.setMinimumSize(QtCore.QSize(350, 400))
        self.tblAnnotations.setMaximumSize(QtCore.QSize(350, 400))
        self.tblAnnotations.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tblAnnotations.setAlternatingRowColors(True)
        self.tblAnnotations.setShowGrid(True)
        self.tblAnnotations.setGridStyle(QtCore.Qt.DashLine)
        self.tblAnnotations.setObjectName("tblAnnotations")
        self.tblAnnotations.horizontalHeader().setHighlightSections(True)
        self.tblAnnotations.verticalHeader().setVisible(False)
        self.tblAnnotations.setColumnCount(3)
        self.tblAnnotations.setRowCount(0)
        self.tblAnnotations.setHorizontalHeaderLabels(['Frame', 'Class', 'Location'])
        self.tblAnnotations.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tblAnnotations.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tblAnnotations.itemSelectionChanged.connect(self.tblSelectionChanged)

        self.dialTMThreshold = QDial(self.gbAnnotations)
        self.dialTMThreshold.setGeometry(QtCore.QRect(180, 525, 50, 50))
        self.dialTMThreshold.setMinimum(0)
        self.dialTMThreshold.setMaximum(100)
        self.dialTMThreshold.setValue(98)
        self.dialTMThreshold.setEnabled(False)
        self.dialTMThreshold.setObjectName("dialTMThreshold")
        self.dialTMThreshold.valueChanged.connect(self.dialTMThresholdChanged)

        self.lblTMThreshold = QtWidgets.QLabel(self.gbAnnotations)
        self.lblTMThreshold.setGeometry(QtCore.QRect(170, 570, 101, 16))
        self.lblTMThreshold.setWordWrap(True)
        self.lblTMThreshold.setObjectName("lblTMThreshold")

        self.cbUseTemplateMatch = QCheckBox(self.gbAnnotations)
        self.cbUseTemplateMatch.setGeometry(QtCore.QRect(20, 530, 180, 40))
        self.cbUseTemplateMatch.setObjectName("cbUseTemplateMatch")
        self.cbUseTemplateMatch.stateChanged.connect(self.tmToggle)

        self.btnDelete = QtWidgets.QPushButton(self.gbAnnotations)
        self.btnDelete.setGeometry(QtCore.QRect(140, 600, 93, 28))
        self.btnDelete.setEnabled(False)
        self.btnDelete.setObjectName("btnDelete")
        self.btnDelete.clicked.connect(self.deleteAnnotation)

        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1071, 26))
        self.menubar.setObjectName("menubar")

        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")

        self.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.menuBtnNewProject = QAction('&New Project', self)
        self.menuBtnNewProject.setShortcut('Ctrl+N')
        self.menuBtnNewProject.setStatusTip('New Project')
        self.menuBtnNewProject.setObjectName("menuBtnNewProject")
        self.menuBtnNewProject.triggered.connect(self.newProject)

        self.menuBtnSaveProject = QAction('&Save Project', self)
        self.menuBtnSaveProject.setShortcut('Ctrl+S')
        self.menuBtnSaveProject.setStatusTip('Save Project')
        self.menuBtnSaveProject.setObjectName("menuBtnSaveProject")
        self.menuBtnSaveProject.triggered.connect(self.saveFile)

        self.menuBtnLoadProject = QAction('&Load Project', self)
        self.menuBtnLoadProject.setShortcut('Ctrl+L')
        self.menuBtnLoadProject.setStatusTip('Load Project')
        self.menuBtnLoadProject.setObjectName("menuBtnLoadProject")
        self.menuBtnLoadProject.triggered.connect(self.loadProject)

        self.menuBtnLoadSec = QAction('Load Secondary', self)
        self.menuBtnLoadSec.setShortcut('Ctrl+O')
        self.menuBtnLoadSec.setStatusTip('Load Secondary')
        self.menuBtnLoadSec.setObjectName("menuBtnLoadSec")
        self.menuBtnLoadSec.triggered.connect(self.loadSec)

        self.menuBtnGenLabelFolder = QAction('&Generate Label Folder', self)
        self.menuBtnGenLabelFolder.setShortcut('Ctrl+G')
        self.menuBtnGenLabelFolder.setStatusTip('Generates Label Folder')
        self.menuBtnGenLabelFolder.setObjectName("menuBtnGenLabelFolder")
        self.menuBtnGenLabelFolder.triggered.connect(self.saveAsLabels)

        self.menuBtnGenOFImages = QAction('Generate OF Filtered Images', self)
        self.menuBtnGenOFImages.setShortcut('Ctrl+F')
        self.menuBtnGenOFImages.setStatusTip('Generate Optical Flow Filtered Images')
        self.menuBtnGenOFImages.setObjectName("menuBtnGenOFImages")
        self.menuBtnGenOFImages.triggered.connect(self.getOFFilter)

        self.menuBtnDeleteStackedBoxes = QAction('Delete stacked boxes', self)
        self.menuBtnDeleteStackedBoxes.setShortcut('Ctrl+D')
        self.menuBtnDeleteStackedBoxes.setStatusTip('Deletes boxes with more than .99 iou')
        self.menuBtnDeleteStackedBoxes.setObjectName("menuBtnDeleteStackedBoxes")
        self.menuBtnDeleteStackedBoxes.triggered.connect(self.deleteStacked)

        self.menuBtnSettings = QAction('Settings', self)
        self.menuBtnSettings.setShortcut('Ctrl+T')
        self.menuBtnSettings.setStatusTip('Settings')
        self.menuBtnSettings.setObjectName("menuBtnSettings")
        # self.menuBtnSettings.triggered.connect(open dialog with setting configs)

        self.menuFile.addAction(self.menuBtnNewProject)
        self.menuFile.addAction(self.menuBtnSaveProject)
        self.menuFile.addAction(self.menuBtnLoadProject)
        self.menuFile.addAction(self.menuBtnLoadSec)

        self.menuTools.addAction(self.menuBtnGenLabelFolder)
        self.menuTools.addAction(self.menuBtnGenOFImages)
        self.menuTools.addAction(self.menuBtnDeleteStackedBoxes)
        self.menuTools.addAction(self.menuBtnSettings)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        if (not os.path.isdir("./Projects")):
            os.makedirs("./Projects")

    def retranslateUi(self, windowRAT):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("windowRAT", "RAT - Rally-video Annotation Tool"))
        self.gbVideoPlayer.setTitle(_translate("windowRAT", "Video Player"))
        self.btnOneFrameFwd.setText(_translate("windowRAT", ">"))
        self.btnOneFrameBwd.setText(_translate("windowRAT", "<"))
        self.btnFiveFramesFwd.setText(_translate("windowRAT", ">>"))
        self.btnFiveFramesBwd.setText(_translate("windowRAT", "<<"))
        self.lblFrameNumber.setText(_translate("windowRAT", "Frame: 0/0"))
        self.lblTMThreshold.setText(_translate("windowRAT", "TM Disabled"))
        self.gbAnnotations.setTitle(_translate("windowRAT", "Annotations"))
        self.btnDelete.setText(_translate("windowRAT", "Delete"))
        self.btnPerformance.setText(_translate("windowRAT", "Performance"))
        self.menuFile.setTitle(_translate("windowRAT", "File"))
        self.menuTools.setTitle(_translate("windowRAT", "Tools"))
        self.menuBtnNewProject.setText(_translate("windowRAT", "New Project"))
        self.menuBtnSaveProject.setText(_translate("windowRAT", "Save Annotations"))
        self.menuBtnLoadProject.setText(_translate("windowRAT", "Load Annotations"))
        self.menuBtnLoadSec.setText(_translate("windowRAT", "Load Secondary"))
        self.menuBtnSettings.setText(_translate("windowRAT", "Settings"))
        self.menuBtnGenOFImages.setText(_translate("windowRAT", "Generate OF Filtered Images"))
        self.menuBtnDeleteStackedBoxes.setText(_translate("windowRAT", "Delete stacked boxes"))
        self.cbUseTemplateMatch.setText(_translate("windowRAT", "Use Template Matching"))
        self.cbMainAnn.setText(_translate("windowRAT", "Main annotations not loaded."))
        self.cbSecAnn.setText(_translate("windowRAT", "Secondary annotations not loaded."))
        self.rbMainAnn.setText(_translate("windowRAT", "List main annotations"))
        self.rbSecAnn.setText(_translate("windowRAT", "List secondary annotations"))
        self.lblRecall.setText(_translate("windowRAT", "Recall: x"))
        self.lblPrecision.setText(_translate("windowRAT", "Precision: x"))

    def keyPressEvent(self, event):
        key = event.key()
        print(key)

        if key == 65:
            self.jumpNFrames(-1)
        if key == 68:
            self.jumpNFrames(1)
        if key == 87:
            self.jumpNFrames(5)
        if key == 83:
            self.jumpNFrames(-5)
        if key == 81:  # q smaller defaultBBox min 5,10
            if not self.demoBoxShowing:
                self.minBoxSize.setX(np.clip(self.minBoxSize.x() - 5, 5, None))
                self.minBoxSize.setY(np.clip(self.minBoxSize.y() - 10, 10, None))
                self.demoBoxP2.setX(self.demoBoxP1.x() + self.minBoxSize.x())
                self.demoBoxP2.setY(self.demoBoxP1.y() + self.minBoxSize.y())
                self.showDemoBox()

        if key == 69:  # e bigger defaultBBox max 50,100
            if not self.demoBoxShowing:
                self.minBoxSize.setX(np.clip(self.minBoxSize.x() + 5, None, 50))
                self.minBoxSize.setY(np.clip(self.minBoxSize.y() + 10, None, 100))
                self.demoBoxP2.setX(self.demoBoxP1.x() + self.minBoxSize.x())
                self.demoBoxP2.setY(self.demoBoxP1.y() + self.minBoxSize.y())
                self.showDemoBox()

        if event.modifiers() & Qt.ControlModifier and not event.modifiers() & Qt.ShiftModifier:
            if key == 67:
                self.copyBoxes()
            elif key == 86:
                self.pasteBoxes(self.initialIdx)
        elif not event.modifiers() & Qt.ControlModifier and not event.modifiers() & Qt.ShiftModifier:
            if key == 67:
                self.clearCurrentFrame()

        if event.modifiers() & Qt.ShiftModifier and event.modifiers() & Qt.ControlModifier:
            if key == 86:
                self.pasteBoxes(self.initialIdx, True)

    def copyBoxes(self):
        self.initialIdx = self.currentFrameIdx
        self.copyBoxList = []
        for bb in self.bBoxList:
            if bb.checkFr(self.currentFrameIdx + 1):
                crds = bb.getCoordList()
                copyBox = MyBBox(QPointF(crds[0], crds[1]), QPointF(crds[2], crds[3]))
                self.copyBoxList.append(copyBox)

    def pasteBoxes(self, initialIdx=-1, all=False):
        if self.initialIdx > -1 and len(self.copyBoxList) > 0:
            if not all:
                for bb in self.copyBoxList:
                    bb.frame = self.currentFrameIdx + 1
                    self.bBoxList.append(bb)
            else:
                for frm in range(self.initialIdx + 2, self.currentFrameIdx + 2):
                    for bb in self.copyBoxList:
                        crds = bb.getCoordList()
                        auxBox = MyBBox(QPointF(crds[0], crds[1]), QPointF(crds[2], crds[3]))
                        auxBox.frame = frm
                        self.bBoxList.append(auxBox)
            self.updateTable()
            self.scene.delCurrentRects()
            self.scene.drawCurrentRects()

    def showDemoBox(self):

        self.startTimer()
        self.demoBoxShowing = True

        self.demoBox = QGraphicsRectItem()
        self.demoBox.setPen(Qt.green)
        self.demoBox.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.demoBox.setRect(QRectF(self.demoBoxP1, self.demoBoxP2))
        self.scene.addItem(self.demoBox)

    def startTimer(self, count=5, interval=100):
        counter = 0

        def handler():
            nonlocal counter
            counter += 1
            if counter >= count:
                timer.stop()
                timer.deleteLater()
                self.scene.removeItem(self.demoBox)
                self.demoBoxShowing = False

        timer = QtCore.QTimer()
        timer.timeout.connect(handler)
        timer.start(interval)

    def tmToggle(self):
        if self.cbUseTemplateMatch.isChecked():
            self.lblTMThreshold.setText('Threshold: {}'.format(self.dialTMThreshold.value()))
            self.useTemplateMatching = True
            self.dialTMThreshold.setEnabled(True)
        else:
            self.lblTMThreshold.setText('TM Disabled')
            self.useTemplateMatching = False
            self.dialTMThreshold.setDisabled(True)

    def openPerfWindow(self):
        # compare secAnn to mainAnn, taking mainAnn as ground truth
        iouThresh = 0.15
        count = 0
        currentFrame = 1
        i = 0

        pendingAnns = []
        pendingAnns = self.secBoxList.copy()

        # recall
        # iterates over groun truth annotations and searches a detection for each ann
        # NOTE THAT THERE CAN BE MULTIPLE DETS ASSIGNED TO A SINGLE GT, in this application the most important is that someone gets detected
        self.bBoxList = sorted(self.bBoxList, key=lambda bbox: bbox.frame, reverse=True)
        for bb in sorted(self.bBoxList, key=lambda bbox: bbox.frame):
            currentFrame = bb.frame
            idxsToDrop = []
            for bb2 in sorted(pendingAnns, key=lambda bbox: bbox.frame):
                if bb.frame == bb2.frame:  # if in frame
                    iou = bb.calcIOU(bb2)
                    print(iou)
                    if (iou > iouThresh):
                        count += 1
                    break
                elif bb.frame >= bb2.frame:  # if frame below
                    pass
                else:  # else break
                    break
        print(count)
        recall = count / len(self.bBoxList)

        count = 0
        # precision
        # iterates over detections and counts how many asserted a GT ann
        for bb in sorted(self.secBoxList, key=lambda bbox: bbox.frame):
            currentFrame = bb.frame
            for bb2 in sorted(self.bBoxList, key=lambda bbox: bbox.frame):
                if bb.frame == bb2.frame:  # if in frame
                    iou = bb.calcIOU(bb2)
                    if (iou > iouThresh):
                        count += 1
                    break
                elif bb.frame >= bb2.frame:  # if frame below
                    pass
                else:  # else break
                    break

        precision = count / len(self.secBoxList)

        self.lblRecall.setText('Recall: {0:.3f}'.format(recall))
        self.lblPrecision.setText('Precision: {0:.3f}'.format(precision))
        self.lblRecall.setVisible(True)
        self.lblPrecision.setVisible(True)

        print("Precision: {0:.3f} \nRecall: {1:.3f}\n".format(precision, recall))

    def dialTMThresholdChanged(self):
        self.tmThresh = (self.dialTMThreshold.value()) / 100
        self.lblTMThreshold.setText('Threshold: {}'.format(self.dialTMThreshold.value()))

    @pyqtSlot(QImage)
    def setImage(self, image):
        pixmap = QPixmap.fromImage(image)
        self.pixmap.setPixmap(pixmap)

    def jumpNFrames(self, n):
        if self.numFrames > 0:
            if self.currentFrameIdx + n < self.numFrames and self.currentFrameIdx + n >= 0:
                self.localIndex += n
                self.currentFrameIdx += n
                for idx, fr in enumerate(os.listdir(self.frameDir)):
                    if idx == self.currentFrameIdx:
                        self.frame = cv2.resize(
                            cv2.cvtColor(cv2.imread('{}{}'.format(self.frameDir, fr)), cv2.COLOR_BGR2RGB),
                            (self.frameWidth, self.frameHeight))
                        break

                self.btnDelete.setEnabled(False)
                self.setFrame()
                self.updateTable()

    def oneFrameFwd(self):
        self.jumpNFrames(1)

    def oneFrameBwd(self):
        self.jumpNFrames(-1)

    def fiveFramesFwd(self):
        self.jumpNFrames(5)

    def fiveFramesBwd(self):
        self.jumpNFrames(-5)

    def sliderMoved(self):
        print(self.hSliderVideoProgress.value())
        self.currentFrameIdx = self.hSliderVideoProgress.value() - 1
        self.btnDelete.setEnabled(False)
        self.lblFrameNumber.setText("Frame: {}/{}".format(self.currentFrameIdx + 1, self.numFrames))

        for idx, fr in enumerate(os.listdir(self.frameDir)):
            if idx == self.currentFrameIdx:
                self.frame = cv2.resize(cv2.cvtColor(cv2.imread('{}{}'.format(self.frameDir, fr)), cv2.COLOR_BGR2RGB),
                                        (self.frameWidth, self.frameHeight))
                break

        self.setFrame(updateSliderPos=False)
        self.updateTable()

    def updateTable(self, selectedIdx=None):

        idxR = 0
        self.tblAnnotations.setRowCount(0)
        self.tableAnnotationIndexer = []
        self.bBoxList = sorted(self.bBoxList, key=lambda bbox: bbox.frame, reverse=True)

        if self.rbMainAnn.isChecked():
            self.tblAnnotations.setRowCount(len(self.bBoxList))
            for bb in self.bBoxList:
                if bb.checkFr(self.currentFrameIdx + 1):
                    self.tblAnnotations.setItem(idxR, 0, QTableWidgetItem(str(bb.frame)))
                    self.tblAnnotations.setItem(idxR, 1, QTableWidgetItem(bb.c))
                    self.tblAnnotations.setItem(idxR, 2, QTableWidgetItem(bb.getLoc(self.frameWidth, self.frameHeight)))
                    self.tableAnnotationIndexer.append(idxR)
                    idxR += 1
            self.tblAnnotations.setRowCount(idxR + 1)

        elif self.rbSecAnn.isChecked():
            self.tblAnnotations.setRowCount(len(self.secBoxList))
            for bb in self.secBoxList:
                if bb.checkFr(self.currentFrameIdx + 1):
                    self.tblAnnotations.setItem(idxR, 0, QTableWidgetItem(str(bb.frame)))
                    self.tblAnnotations.setItem(idxR, 1, QTableWidgetItem(bb.c))
                    self.tblAnnotations.setItem(idxR, 2, QTableWidgetItem(bb.getLoc(self.frameWidth, self.frameHeight)))
                    self.tableAnnotationIndexer.append(idxR)
                    idxR += 1
            self.tblAnnotations.setRowCount(idxR + 1)
            if selectedIdx is not None:
                self.btnDelete.setEnabled(True)

    def deleteAnnotation(self):
        del self.bBoxList[self.selectedBoxIdx]

        annCountIdx = int(np.ceil(self.currentFrameIdx / self.numFrames * 95))
        self.annCount[annCountIdx] -= 1
        self.drawAnnCount()

        self.updateTable()
        self.scene.itemSelected = False
        self.scene.delCurrentRects()
        self.scene.drawCurrentRects()
        self.btnDelete.setEnabled(False)

    def clearCurrentFrame(self):
        toDelIndexes = []

        for i, bbox in enumerate(self.bBoxList):
            if bbox.checkFr(self.currentFrameIdx + 1):
                toDelIndexes.append(i)

        print(toDelIndexes)

        for idx in sorted(toDelIndexes, reverse=True):
            del self.bBoxList[idx]

        self.scene.delCurrentRects()
        self.updateTable()

    def setFrame(self, updateSliderPos=True):
        qImg = QImage(self.frame, self.frameWidth, self.frameHeight, self.bytesPerLine, QImage.Format_RGB888)
        self.pixmap.setPixmap(QPixmap.fromImage(qImg))
        self.lblFrameNumber.setText("Frame: {}/{}".format(self.currentFrameIdx + 1, self.numFrames))
        if updateSliderPos:
            self.hSliderVideoProgress.setValue(self.currentFrameIdx + 1)

        self.scene.delCurrentRects()
        self.scene.drawCurrentRects()
        self.updateTable()

    def initVideo(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        self.btnOneFrameFwd.setEnabled(True)
        self.btnOneFrameBwd.setEnabled(True)
        self.btnFiveFramesFwd.setEnabled(True)
        self.btnFiveFramesBwd.setEnabled(True)
        self.currentFrameIdx = 0
        self.hSliderVideoProgress.setValue(0)

        # partial loading vars setup
        self.numFrames = len(os.listdir(self.frameDir))
        print(self.numFrames)

        for idx, fr in enumerate(os.listdir(self.frameDir)):
            if idx == self.currentFrameIdx:
                print(fr)
                self.frame = cv2.resize(cv2.cvtColor(cv2.imread('{}{}'.format(self.frameDir, fr)), cv2.COLOR_BGR2RGB),
                                        (self.frameWidth, self.frameHeight))
                break

        self.playerState = 'videoLoaded'
        self.gvFrameDisplay.setEnabled(True)

        # convert first frame to qImage and display
        self.hSliderVideoProgress.setMaximum(self.numFrames - 1)
        self.setFrame()
        QApplication.restoreOverrideCursor()

    def newProject(self):

        # if a file is loaded, ask to save
        abortLoad = False
        if self.playerState != 'empty':
            qm = QMessageBox
            ret = QMessageBox.question(self, '', "Do you want to save before opening a new project?",
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if ret == QMessageBox.Yes:
                self.saveFile()
            elif ret == QMessageBox.Cancel:
                abortLoad = True

        if not abortLoad:

            self.fileName, _ = QFileDialog.getOpenFileName(self, "Select Video for Project", QDir.currentPath(),
                                                           "MP4 Video (*.mp4)")

            if self.fileName != '':

                # TODO: Move to a method in utils lib.
                self.strippedName = self.fileName[:-4]
                i = 0
                for c in self.fileName:
                    if (c == '/'):
                        lastPos = i
                    i += 1
                self.strippedName = self.strippedName[lastPos + 1:]  # name without directory and extension

                text, okPressed = QtWidgets.QInputDialog.getText(None, "R.A.T.", "Project Author:",
                                                                 QtWidgets.QLineEdit.Normal, "")
                if okPressed and text != '':
                    self.author = text

                    if not os.path.isdir("./Projects/{}".format(self.strippedName)):
                        os.makedirs("./Projects/{}".format(self.strippedName))

                    if not os.path.isdir("./Projects/{}/images".format(self.strippedName)):
                        os.makedirs("./Projects/{}/images".format(self.strippedName))
                        os.makedirs("./Projects/{}/filterImages".format(self.strippedName))
                        os.makedirs("./Projects/{}/labels".format(self.strippedName))

                    self.frameDir = "./Projects/{}/images/".format(self.strippedName)
                    print(len(os.listdir(self.frameDir)))
                    print(self.fileName, self.frameDir)

                    if len(os.listdir(self.frameDir)) == 0:
                        os.system('ffmpeg -i "{}" -qscale:v 2 "{}"%12d.jpg'.format(self.fileName, self.frameDir))

                    self.initVideo()

                    with open('./Projects/{}/{}.ann'.format(self.strippedName, self.author), 'w') as f:
                        f.write('author:§{}§ lenght:§0§ fps:§d§\n'.format(self.author))

                    self.playerState = 'videoLoaded'
                    self.cbMainAnn.setChecked(True)
                    self.cbMainAnn.setText('Main annotations loaded')

    def tblSelectionChanged(self):
        items = self.tblAnnotations.selectedIndexes()

        if (len(items) > 0):
            self.selectedTableIdx = self.tblAnnotations.selectionModel().selectedRows()[0].row()
            self.selectedBoxIdx = self.tableAnnotationIndexer[self.selectedTableIdx]

            for bb in self.bBoxList:
                if bb.col is not Qt.red:
                    bb.col = Qt.red
            self.bBoxList[self.selectedBoxIdx].col = Qt.green

            self.btnDelete.setEnabled(True)
            self.scene.delCurrentRects()
            self.scene.drawCurrentRects()
        else:
            self.btnDelete.setEnabled(False)

    def loadProject(self):
        sep = '§'
        fileLenght = ''
        sepCount = 0

        # if a file is loaded, ask to save
        abortLoad = False
        if self.playerState != 'empty':
            qm = QMessageBox
            ret = QMessageBox.question(self, '', "Do you want to save before loading a project?",
                                       QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

            if ret == QMessageBox.Yes:
                self.saveFile()
            elif ret == QMessageBox.Cancel:
                abortLoad = True

        if not abortLoad:

            annFileName, _ = QFileDialog.getOpenFileName(self, "Select Project for loading", QDir.currentPath(),
                                                         "Annotation file (*.ann)")

            if annFileName != '':
                self.strippedName = annFileName.split(sep='/')[-2]
                self.frameDir = "./Projects/{}/images/".format(self.strippedName)
                self.fileName = None
                self.numFrames = len(os.listdir(self.frameDir))
                self.author = ''
                print(self.strippedName)
                fps = ''
                self.bBoxList = []
                count = 0

                with open(annFileName, "r") as f:
                    for line in f:

                        if line[0] is 'a':
                            # first line
                            for c in line[8:]:
                                if c is sep:
                                    sepCount += 1
                                if sepCount is 0:
                                    self.author += c
                                if sepCount is 2:
                                    fileLenght += c
                                if sepCount is 4:
                                    fps += c
                        elif line[0] is '0':
                            # annotation lines
                            items = line.split()
                            self.bBoxList.append(MyBBox(QPointF(float(items[1]), float(items[2])),
                                                        QPointF(float(items[3]), float(items[4])),
                                                        fr=self.currentFrameIdx + 1))
                            count += 1
                        elif len(line) is 0:
                            # eof
                            break
                        else:
                            # frame number lines
                            self.currentFrameIdx = int(line) - 1
                            count = 0

                self.currentFrameIdx = 0
                self.initVideo()
                self.updateAnnCount()

                self.updateTable()
                self.setFrame()
                self.scene.drawCurrentRects()

                self.playerState = 'videoLoaded'

                self.cbMainAnn.setChecked(True)
                self.cbMainAnn.setText('Main annotations loaded')

                if self.cbMainAnn.isChecked() and self.cbSecAnn.isChecked():
                    self.btnPerformance.setEnabled(True)

    def loadSec(self):
        sep = '§'
        fileLenght = ''
        self.secBoxList = []
        self.currentFrameIdx = 0
        sepCount = 0
        annfileName, _ = QFileDialog.getOpenFileName(self, "Select Annotation", QDir.currentPath(),
                                                     "Annotation file (*.ann)")
        with open(annfileName, "r") as f:
            for line in f:
                if line[0] is 'a':
                    # first line
                    for c in line[8:]:
                        if c is sep:
                            sepCount += 1
                        if sepCount is 0:
                            self.author += c
                        if sepCount is 2:
                            fileLenght += c
                elif line[0] is '0':
                    # annotation lines
                    items = line.split()
                    self.secBoxList.append(
                        MyBBox(QPointF(float(items[1]), float(items[2])), QPointF(float(items[3]), float(items[4])),
                               fr=self.currentFrameIdx + 1, col=Qt.cyan))

                elif len(line) is 0:
                    # eof
                    break
                else:
                    # frame number lines
                    self.currentFrameIdx = int(line) - 1

        print('labels: {}'.format(len(self.secBoxList)))
        self.rbSecAnn.setEnabled(True)
        self.currentFrameIdx = 0
        self.updateTable()
        self.setFrame()
        self.scene.delCurrentRects()
        self.scene.drawCurrentRects()

        self.cbSecAnn.setChecked(True)
        self.cbSecAnn.setText('Secondary annotations loaded')

        if self.cbMainAnn.isChecked() and self.cbSecAnn.isChecked():
            self.btnPerformance.setEnabled(True)

    def saveFile(self):

        if self.playerState != 'empty':
            actualFrame = 0
            fName = '{}.ann'.format(self.author)
            saveDir = "./Projects/{}/".format(self.strippedName)
            if (not os.path.isdir(saveDir)):
                os.makedirs(saveDir)

            if self.cbSecAnn.isChecked():
                qm = QMessageBox
                ret = QMessageBox.question(self, '', "Do you want to merge with secondary annotations?",
                                           QMessageBox.Yes | QMessageBox.No)

                # ask author everytime? or implement save as.. button
                # text, okPressed = QtWidgets.QInputDialog.getText(None, "R.A.T.", "Project Author:", QtWidgets.QLineEdit.Normal, "")
                # if okPressed and text != '':
                #     self.author = text

                if ret == QMessageBox.Yes:
                    # get all annotations to one list
                    auxList = self.bBoxList.copy()
                    for bb in self.secBoxList:
                        auxList.append(bb)

                    auxList = sorted(auxList, key=lambda bbox: bbox.frame, reverse=False)

                    with open('{}{}'.format(saveDir, fName), 'w') as f:
                        f.write('author:§{}§ lenght:§{}§ fps:§d§\n'.format(self.author, len(auxList)))
                        for bb in auxList:
                            ann = '0 {} {} {} {}\n'.format(str(bb.point1.x()), str(bb.point1.y()), str(bb.point2.x()),
                                                           str(bb.point2.y()))

                            if bb.frame != actualFrame:
                                actualFrame = bb.frame
                                f.write('{}\n'.format(actualFrame))

                            f.write(ann)

                elif ret == QMessageBox.No:
                    with open('{}{}'.format(saveDir, fName), 'w') as f:
                        f.write('author:§{}§ lenght:§{}§ fps:§d§\n'.format(self.author, len(self.bBoxList)))
                        for bb in self.bBoxList:
                            ann = '0 {} {} {} {}\n'.format(str(bb.point1.x()), str(bb.point1.y()), str(bb.point2.x()),
                                                           str(bb.point2.y()))

                            if bb.frame != actualFrame:
                                actualFrame = bb.frame
                                f.write('{}\n'.format(actualFrame))

                            f.write(ann)
            else:
                with open('{}{}'.format(saveDir, fName), 'w') as f:
                    f.write('author:§{}§ lenght:§{}§ fps:§d§\n'.format(self.author, len(self.bBoxList)))
                    for bb in self.bBoxList:
                        ann = '0 {} {} {} {}\n'.format(str(bb.point1.x()), str(bb.point1.y()), str(bb.point2.x()),
                                                       str(bb.point2.y()))

                        if bb.frame != actualFrame:
                            actualFrame = bb.frame
                            f.write('{}\n'.format(actualFrame))

                        f.write(ann)

    def getNbr(self, number):
        number = str(number)
        while (len(number) < 12):
            number = "0{}".format(number)
        return number

    def saveAsLabels(self):
        actualFrame = 0
        for bb in self.bBoxList:

            ann = bb.getLabelNotation(self.frameWidth, self.frameHeight)

            if bb.frame != actualFrame:
                actualFrame = bb.frame
                number = self.getNbr(actualFrame)
                fName = "./Projects/{}/labels/{}.txt".format(self.strippedName, number)
                with open(fName, 'w') as f:
                    f.write('')

            with open(fName, 'a') as f:
                f.write(ann)

        with open("./Projects/{}/FrameList.txt".format(self.strippedName), 'w') as fList:
            for i in range(1, self.numFrames):
                number = self.getNbr(i)
                fList.write("./Projects/{}/images/{}.jpg\n".format(self.strippedName, number))

    def matchTemplate(self, tCoords):
        imgs = []
        methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF',
                   'cv2.TM_SQDIFF_NORMED']
        mthdIdx = 5
        meth = eval(methods[mthdIdx])
        fr = self.currentFrameIdx

        for i in range(self.tmFrameSpan):
            fr += 1
            print('{}{}.jpg'.format(self.frameDir, self.getNbr(fr)))
            imgs.append(cv2.resize(
                cv2.cvtColor(cv2.imread('{}{}.jpg'.format(self.frameDir, self.getNbr(fr))), cv2.COLOR_BGR2RGB),
                (self.frameWidth, self.frameHeight)))

        templ = self.frame[int(tCoords[1]):int(tCoords[3]), int(tCoords[0]):int(tCoords[2])]
        print(templ)

        tmplH, tmplW, _ = templ.shape
        fr = self.currentFrameIdx + 1

        for im in imgs:

            res = cv2.matchTemplate(im, templ, meth)
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res)

            print(minVal, maxVal, minLoc, maxLoc)

            if ((1 - self.tmThresh) > minVal):
                topLeft = minLoc
                botRight = (topLeft[0] + tmplW, topLeft[1] + tmplH)
                aux = MyBBox(point1=QPointF(topLeft[0], topLeft[1]), point2=QPointF(botRight[0], botRight[1]), fr=fr)
                self.bBoxList.append(aux)
            fr += 1

    def getOFFilter(self):
        filterThresh = 0.08
        c = 0
        if self.numFrames > 0:
            filterThresh = int(filterThresh * 255)
            testLenght = int(self.numFrames * 0.02)  # 2% test lenght by default
            filterSum = np.zeros(shape=(1080, 1920), dtype=np.float32)
            frameDir = "./Projects/{}/images/".format(self.strippedName)

            tMaskGen = time.time()

            for i in range(0, testLenght):
                r = random.randint(1, self.numFrames - 1)
                file = '{}.jpg'.format(self.getNbr(r))
                nFile = '{}.jpg'.format(self.getNbr(r + 1))

                im1 = cv2.cvtColor(cv2.imread(os.path.join(frameDir, file)), cv2.COLOR_BGR2GRAY)
                im2 = cv2.cvtColor(cv2.imread(os.path.join(frameDir, nFile)), cv2.COLOR_BGR2GRAY)

                flow = cv2.calcOpticalFlowFarneback(im1, im2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                gray = np.zeros((flow.shape[0], flow.shape[1]),
                                np.float32)  # Converting only the magnitude of OF to grayscale image
                gray = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
                filterSum += gray

            filterSum /= testLenght  # normalize on sample length
            # loop over the image
            for y in range(0, 1080):
                for x in range(0, 1920):
                    # threshold the pixel
                    # print(filterSum[y, x])
                    filterSum[y, x] = 255 if filterSum[y, x] >= filterThresh else 0
                    if filterSum[y, x] == 255:
                        c += 1

            cv2.imwrite('./Projects/{}/rawFilter.png'.format(self.strippedName), filterSum)
            print(c / (1920 * 1080))

            kernel = np.ones((27, 27),
                             np.uint8)  # Tested various filter sizes, as the images have relatively high res, 13 performs good.
            erodedImg = cv2.erode(filterSum, kernel, iterations=3)  # 3 iters
            filterSum = cv2.dilate(erodedImg, kernel, iterations=1)

            cv2.imwrite('./Projects/{}/filter.png'.format(self.strippedName), filterSum)

            filterSum = filterSum.astype(np.uint8)
            filtered = 0
            for n in np.reshape(filterSum, [-1]):
                if n == 0:
                    filtered += 1

            print('Filtering Ratio: {}'.format(filtered / (1920 * 1080)))
            print('Mask generated in: {:10.3f} sec.'.format(time.time() - tMaskGen))

            # tMaskApply = time.time()
            # i=0
            # frameList = os.listdir('./Projects/{}/images/'.format(self.strippedName))
            # for f in frameList:
            #     auxIm = cv2.imread('./Projects/{}/images/{}'.format(self.strippedName, f))
            #     res = cv2.bitwise_and(auxIm,auxIm,mask = filterSum) #a lot more effective than my c-way of applying the mask
            #     cv2.imwrite('./Projects/{}/filterImages/{}.jpg'.format(self.strippedName, self.getNbr(i)),cv2.cvtColor( res, cv2.COLOR_RGB2BGR))
            #     i += 1
            # print('Mask applied to {} frames in: {:10.3f} sec.'.format(len(frameList), (time.time() - tMaskGen)))

    def deleteStacked(self):
        iouThresh = 0.95
        checkedIdx = 1
        idxsToDel = []
        for bb in self.bBoxList:
            for j in range(checkedIdx, len(self.bBoxList)):
                bb2 = self.bBoxList[j]
                if (bb.checkFr(bb2.frame)):
                    iou = bb.calcIOU(bb2)
                    if (iou > iouThresh):
                        idxsToDel.append(j)
            checkedIdx += 1

        idxsToDel = set(idxsToDel)
        print(len(idxsToDel))
        for idx in sorted(idxsToDel, reverse=True):
            del self.bBoxList[idx]
        self.updateTable()
        self.scene.delCurrentRects()
        self.scene.drawCurrentRects()

    def updateAnnCount(self):

        bBoxCount = np.zeros([self.numFrames + 1])
        ratio = int(np.floor(self.numFrames / 95))  # How many frames are considered to paint one cell.
        bIdx = 0  # box index, used for mapping
        self.annCount[0] = 0  # all other indexes are set to 0 in the second for loop

        for box in self.bBoxList:
            bBoxCount[box.frame] += 1

        for i, c in enumerate(bBoxCount):
            if i > 0 and i % ratio == 0 and bIdx < 95:
                bIdx += 1
                self.annCount[bIdx] = 0

            self.annCount[bIdx] += int(c)

        self.drawAnnCount()
        print(self.annCount)

    def drawAnnCount(self):
        self.tagScene.clear()

        for i, n in enumerate(self.annCount):
            if n == 0:
                col = Qt.white
            elif n > 0 and n < 50:
                col = Qt.yellow
            elif n > 49 and n < 200:
                col = Qt.green
            elif n > 199:
                col = Qt.blue

            iPoint = QPointF(0.0 + i * 10, 0.0)
            fPoint = QPointF((i + 1) * 10, 10.0)

            box = QRectF(iPoint, fPoint)

            tmpBox = QtWidgets.QGraphicsRectItem(QtCore.QRectF(iPoint, fPoint))
            tmpBox.setBrush(col)
            tmpBox.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
            self.tagScene.addItem(tmpBox)
        self.tagScene.update()
