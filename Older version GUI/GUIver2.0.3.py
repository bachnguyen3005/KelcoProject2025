# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUIver1.1.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter
from datetime import datetime

import cv2


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(650, 457)
        MainWindow.setMouseTracking(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../../../../Documents/PlatformIO/Projects/kelco_test_001/beta.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowOpacity(1.0)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("background-color: qlineargradient(spread:reflect, x1:0, y1:1, x2:0.957447, y2:1, stop:0 rgba(136, 138, 133, 255), stop:1 rgba(255, 255, 255, 255));")
        MainWindow.setIconSize(QtCore.QSize(40, 40))
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(85, 87, 83, 255), stop:1 rgba(255, 255, 255, 255));")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setStyleSheet("background-color: rgb(211, 215, 207);")
        self.tabWidget.setObjectName("tabWidget")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.scrollArea = QtWidgets.QScrollArea(self.tab_3)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 600, 321))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.calLCDNumber = QtWidgets.QLCDNumber(self.scrollAreaWidgetContents)
        self.calLCDNumber.setStyleSheet("background-color: rgb(252, 233, 79);")
        self.calLCDNumber.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.calLCDNumber.setProperty("intValue", 0)
        self.calLCDNumber.setObjectName("calLCDNumber")
        self.gridLayout_2.addWidget(self.calLCDNumber, 2, 1, 1, 5)
        self.stopButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(35)
        self.stopButton.setFont(font)
        self.stopButton.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.stopButton.setAutoFillBackground(False)
        self.stopButton.setStyleSheet("background-color: rgb(204, 0, 0);")
        self.stopButton.setObjectName("stopButton")
        self.gridLayout_2.addWidget(self.stopButton, 0, 1, 1, 1)
        self.startButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(35)
        self.startButton.setFont(font)
        self.startButton.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.startButton.setAutoFillBackground(False)
        self.startButton.setStyleSheet("background-color: rgb(138, 226, 52);")
        self.startButton.setObjectName("startButton")
        self.gridLayout_2.addWidget(self.startButton, 0, 0, 1, 1)
        self.calLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.calLabel.setFont(font)
        self.calLabel.setStyleSheet("background-color: rgb(252, 233, 79);")
        self.calLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.calLabel.setObjectName("calLabel")
        self.gridLayout_2.addWidget(self.calLabel, 3, 0, 1, 1)
        self.kpaLCDNumber = QtWidgets.QLCDNumber(self.scrollAreaWidgetContents)
        self.kpaLCDNumber.setStyleSheet("background-color: rgb(252, 233, 79);")
        self.kpaLCDNumber.setSmallDecimalPoint(False)
        self.kpaLCDNumber.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.kpaLCDNumber.setProperty("value", 0.0)
        self.kpaLCDNumber.setProperty("intValue", 0)
        self.kpaLCDNumber.setObjectName("kpaLCDNumber")
        self.gridLayout_2.addWidget(self.kpaLCDNumber, 3, 1, 1, 5)
        self.kpaLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.kpaLabel.setFont(font)
        self.kpaLabel.setStyleSheet("background-color: rgb(252, 233, 79);\n"
"")
        self.kpaLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.kpaLabel.setObjectName("kpaLabel")
        self.gridLayout_2.addWidget(self.kpaLabel, 2, 0, 1, 1)
        self.resetButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setFamily("Ubuntu Mono")
        font.setPointSize(30)
        font.setBold(False)
        font.setWeight(50)
        self.resetButton.setFont(font)
        self.resetButton.setStyleSheet("background-color: rgb(114, 159, 207);")
        self.resetButton.setObjectName("resetButton")
        self.gridLayout_2.addWidget(self.resetButton, 0, 2, 1, 1)
        self.captureAnDetectButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.captureAnDetectButton.setFont(font)
        self.captureAnDetectButton.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.captureAnDetectButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.captureAnDetectButton.setStyleSheet("background-color: rgb(252, 175, 62);")
        self.captureAnDetectButton.setObjectName("captureAnDetectButton")
        self.gridLayout_2.addWidget(self.captureAnDetectButton, 0, 3, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_3.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab_4)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.viewButton = QtWidgets.QPushButton(self.tab_4)
        self.viewButton.setStyleSheet("background-color: rgb(173, 127, 168);")
        self.viewButton.setObjectName("viewButton")
        self.gridLayout_4.addWidget(self.viewButton, 1, 0, 1, 1)
        self.closeButton = QtWidgets.QPushButton(self.tab_4)
        self.closeButton.setStyleSheet("background-color: rgb(239, 41, 41);")
        self.closeButton.setObjectName("closeButton")
        self.gridLayout_4.addWidget(self.closeButton, 1, 1, 1, 1)
        self.webcamFrame = QtWidgets.QLabel(self.tab_4)
        self.webcamFrame.setText("")
        self.webcamFrame.setObjectName("label")
        self.gridLayout_4.addWidget(self.webcamFrame, 0, 0, 1, 2)
        self.tabWidget.addTab(self.tab_4, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 650, 26))
        self.menubar.setStyleSheet("")
        self.menubar.setObjectName("menubar")
        self.menuMain_layout = QtWidgets.QMenu(self.menubar)
        self.menuMain_layout.setStyleSheet("background-color: rgb(136, 138, 133);")
        self.menuMain_layout.setObjectName("menuMain_layout")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuMain_layout.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.cap = cv2.VideoCapture(2)

        self.viewButton.clicked.connect(self.startWebcam)

        self.closeButton.clicked.connect(self.stop_webcam) 

        self.captureAnDetectButton.clicked.connect(self.snapshot)       

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Automated Calibration System GUI"))
        self.stopButton.setText(_translate("MainWindow", "Estop"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.calLabel.setText(_translate("MainWindow", "Cal"))
        self.kpaLabel.setText(_translate("MainWindow", "Kpa"))
        self.resetButton.setText(_translate("MainWindow", "Reset"))
        self.captureAnDetectButton.setText(_translate("MainWindow", "Capture"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Control GUI"))
        self.viewButton.setText(_translate("MainWindow", "View"))
        self.closeButton.setText(_translate("MainWindow", "Close"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Webcam"))
        self.menuMain_layout.setTitle(_translate("MainWindow", "Main layout"))

    def startWebcam(self):
        # Set up timer for updating the frame
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update frame every 30 ms

    def stop_webcam(self):
        self.timer.stop()
        self.cap.release()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:      
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            qt_pixmap = QPixmap.fromImage(qt_image)
            self.webcamFrame.setPixmap(qt_pixmap)
            self.webcamFrame.setAlignment(Qt.AlignCenter)
    def startWebcam(self):
        # Set up timer for updating the frame
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update frame every 30 ms

    def stop_webcam(self):
        self.timer.stop()
        self.cap.release()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:      
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            qt_pixmap = QPixmap.fromImage(qt_image)
            self.webcamFrame.setPixmap(qt_pixmap)
            self.webcamFrame.setAlignment(Qt.AlignCenter)
    def startWebcam(self):
        # Set up timer for updating the frame
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update frame every 30 ms

    def stop_webcam(self):
        self.timer.stop()
        self.cap.release()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:      
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            qt_pixmap = QPixmap.fromImage(qt_image)
            self.webcamFrame.setPixmap(qt_pixmap)
            self.webcamFrame.setAlignment(Qt.AlignCenter)
            self.draw_red_rectangle()

    def draw_red_rectangle(self):
        # Create a QPixmap to paint on, using the same size as the webcam_label
        pixmap = self.webcamFrame.pixmap()
        if pixmap is None:
            return  # Safety check to ensure pixmap exists

        painter = QPainter(pixmap)
        
        # Set pen for drawing the hollow rectangle border
        pen = painter.pen()
        pen.setColor(Qt.red)       # Set the border color to red
        pen.setWidth(3)            # Set the border width to 3 pixels
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)  # Ensure no fill for the rectangle

        # Calculate the size and position for the hollow rectangle
        rect_width = 550
        rect_height = 140 
        rect_x = 50
        rect_y = 150
        
        # Draw the hollow rectangle
        painter.drawRect(rect_x, rect_y, rect_width, rect_height)
        
        # End painting
        painter.end()
        
        # Update the label with the modified pixmap
        self.webcamFrame.setPixmap(pixmap)


    def snapshot(self):
        ret, frame = self.cap.read()
        if ret:
            # Calculate the size and position for the rectangle (same as in draw_red_rectangle)
            rect_width = 550 
            rect_height = 140 
            rect_x = 100
            rect_y = 150

            # Crop the frame to the size of the red rectangle
            cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename_original = f"SnapShotImages/processed_snapshot_uncropped{timestamp}.jpg"
            image_filename = f"SnapShotImages/processed_snapshot{timestamp}.jpg"         
            # Save the processed image for OCR
            cv2.imwrite(image_filename, cropped_frame)
            cv2.imwrite(image_filename_original, frame)
            # Perform OCR on the cropped image
            # img_with_text, extracted_text = self.ocr_processor.run_ocr(image_filename)
            # result = self.ocr_processor.run_ocr_simple(image_filename)
            # print(result[1])
            # result_int = int(result[1])
            # print(result_int)
            # Convert the processed image to QImage

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
