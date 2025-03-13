# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUIver2.0.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter
import serial
from ocr import OCRProcessor
from utils import SerialCommunicator
# from playsound import playsound
import cv2
from datetime import datetime

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 480)
        MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        MainWindow.setMouseTracking(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../../../../Documents/PlatformIO/Projects/kelco_test_001/beta.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowOpacity(1.0)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("background-color: rgb(136, 138, 133);")
        MainWindow.setIconSize(QtCore.QSize(40, 40))
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        self.centralwidget.setStyleSheet("selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(85, 87, 83, 255), stop:1 rgba(255, 255, 255, 255));")
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
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
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 650, 344))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.kpaLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(40)
        font.setBold(True)
        font.setWeight(75)
        self.kpaLabel.setFont(font)
        self.kpaLabel.setStyleSheet("background-color: rgb(252, 233, 79);\n"
"")
        self.kpaLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.kpaLabel.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.kpaLabel.setLineWidth(1)
        self.kpaLabel.setScaledContents(False)
        self.kpaLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.kpaLabel.setObjectName("kpaLabel")
        self.gridLayout_2.addWidget(self.kpaLabel, 2, 0, 1, 1)
        self.exitButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(30)
        self.exitButton.setFont(font)
        self.exitButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.exitButton.setAutoFillBackground(False)
        self.exitButton.setStyleSheet("background-color: rgb(245, 121, 0);")
        self.exitButton.setObjectName("exitButton")
        self.gridLayout_2.addWidget(self.exitButton, 0, 3, 1, 1)
        self.startButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(30)
        self.startButton.setFont(font)
        self.startButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.startButton.setAutoFillBackground(False)
        self.startButton.setStyleSheet("background-color: rgb(138, 226, 52);")
        self.startButton.setObjectName("startButton")
        self.gridLayout_2.addWidget(self.startButton, 0, 0, 1, 1)
        self.kpaLCDNumber = QtWidgets.QLCDNumber(self.scrollAreaWidgetContents)
        self.kpaLCDNumber.setStyleSheet("background-color: rgb(252, 233, 79);")
        self.kpaLCDNumber.setSmallDecimalPoint(False)
        self.kpaLCDNumber.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.kpaLCDNumber.setProperty("value", 0.0)
        self.kpaLCDNumber.setProperty("intValue", 0)
        self.kpaLCDNumber.setObjectName("kpaLCDNumber")
        self.gridLayout_2.addWidget(self.kpaLCDNumber, 2, 1, 1, 3)
        self.calLCDNumber = QtWidgets.QLCDNumber(self.scrollAreaWidgetContents)
        self.calLCDNumber.setStyleSheet("background-color: rgb(252, 233, 79);")
        self.calLCDNumber.setFrameShape(QtWidgets.QFrame.Box)
        self.calLCDNumber.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.calLCDNumber.setProperty("intValue", 0)
        self.calLCDNumber.setObjectName("calLCDNumber")
        self.gridLayout_2.addWidget(self.calLCDNumber, 3, 1, 1, 3) #Change to 3, 1, 1, 3
        self.calLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(40)
        font.setBold(True)
        font.setWeight(75)
        self.calLabel.setFont(font)
        self.calLabel.setStyleSheet("background-color: rgb(252, 233, 79);")
        self.calLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.calLabel.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.calLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.calLabel.setObjectName("calLabel")
        self.gridLayout_2.addWidget(self.calLabel, 3, 0, 1, 1)
        self.resetButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(30)
        self.resetButton.setFont(font)
        self.resetButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.resetButton.setAutoFillBackground(False)
        self.resetButton.setStyleSheet("background-color: rgb(52, 101, 164);")
        self.resetButton.setObjectName("resetButton")
        self.gridLayout_2.addWidget(self.resetButton, 0, 1, 1, 1)
        self.stopButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(30)
        self.stopButton.setFont(font)
        self.stopButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.stopButton.setAutoFillBackground(False)
        self.stopButton.setStyleSheet("background-color: rgb(204, 0, 0);")
        self.stopButton.setObjectName("stopButton")
        self.gridLayout_2.addWidget(self.stopButton, 0, 2, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_3.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab_4)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.tab_4)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 650, 344))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_2)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.viewButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents_2)
        self.viewButton.setStyleSheet("background-color: rgb(173, 127, 168);")
        self.viewButton.setObjectName("viewButton")
        self.gridLayout_5.addWidget(self.viewButton, 2, 0, 1, 1)
        self.closeButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents_2)
        self.closeButton.setStyleSheet("background-color: rgb(239, 41, 41);")
        self.closeButton.setObjectName("closeButton")
        self.gridLayout_5.addWidget(self.closeButton, 2, 1, 1, 1)
        self.webcamFrame = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.webcamFrame.setText("")
        self.webcamFrame.setObjectName("webcamFrame")
        self.gridLayout_5.addWidget(self.webcamFrame, 0, 0, 1, 2)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.gridLayout_4.addWidget(self.scrollArea_2, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_4, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 700, 26))
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
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.is_webcam_open = False

        self.is_webcam_open_first_time = False
        self.ocr_processor = OCRProcessor()

        # self.arduino = SerialCommunicator(port='/dev/ttyUSB0', baudrate=115200, timeout=1)

        self.cap = cv2.VideoCapture(2)

        self.viewButton.clicked.connect(self.startWebcam)

        self.closeButton.clicked.connect(self.stop_webcam)

        self.resetButton.clicked.connect(self.confirmReset)

        self.exitButton.clicked.connect(self.confirmExit)

        self.startButton.clicked.connect(self.confirmStart)

        self.stopButton.clicked.connect(self.snapshot)

    def start(self):

        if self.is_webcam_open:

            self.arduino.send_command('A')  # Extend the actuator 2 and 3 and pump ON

            command2check = "L"  # Check command from arduino
            response = self.arduino.read_command()
            print(response)

            # Timer for after_delay execution
            self.delay_timer = QTimer()
            self.delay_timer.setSingleShot(True)  # Make sure the timer fires only once
            self.delay_timer.timeout.connect(lambda: self.after_delay(response, command2check))
            self.delay_timer.start(5000)  # 5-second delay before calling after_delay
        else: 
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Could not open webcam. Click View button again.")

    def after_delay(self, response, command2check):
        if response == command2check:

            ret, frame = self.cap.read()
            if ret:
                # Process and crop the frame for OCR
                rect_width = 500 
                rect_height = 140 
                rect_x = 70
                rect_y = 150
                cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]


                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"SnapShotImages/processed_snapshot_LOCK2UNLOCK{timestamp}.jpg"

                # Save the processed image for OCR
                cv2.imwrite(image_filename, cropped_frame)

                # Perform OCR on the cropped image
                img_with_text, extracted_text = self.ocr_processor.run_ocr(image_filename)

                # Perform further actions based on OCR result
                if extracted_text.strip() == "LOCKED":

                    # playsound('Sound/LockedModeVer2.mp3')


                    self.stop_timer = QTimer()
                    self.stop_timer.setSingleShot(True)
                    self.stop_timer.timeout.connect(lambda: self.arduino.send_command('K'))
                    self.stop_timer.start(3000)  # 3-second delay before retracting actuator 2 and 3

                    # Timer for second action: retract_button_2.click() (Turn off the pump controller)
                    self.retract_timer = QTimer()
                    self.retract_timer.setSingleShot(True)
                    self.retract_timer.timeout.connect(lambda: self.arduino.send_command('C')) #Pump off
                    self.retract_timer.start(6000)  # 6-second delay

                    # Timer for third action: send_command('R') to extend actuators 2 and 3
                    self.command_timer = QTimer()
                    self.command_timer.setSingleShot(True)
                    self.command_timer.timeout.connect(lambda: self.arduino.send_command('R')) #Extend Act2 and Act3
                    self.command_timer.start(9000)  # 9-second delay

                    # Timer for fourth action: Turn off the controller
                    self.pumpOn_timer = QTimer()
                    self.pumpOn_timer.setSingleShot(True)
                    self.pumpOn_timer.timeout.connect(lambda: self.arduino.send_command('B')) #Pump on
                    self.pumpOn_timer.start(12000)  # 12-second delay

                    # Timer for retracting actuator 2 and 3 again
                    self.retract_time_2 = QTimer()
                    self.retract_time_2.setSingleShot(True)
                    self.retract_time_2.timeout.connect(lambda: self.arduino.send_command('K')) #Retract Act2 and Act3
                    self.retract_time_2.start(16000)  # 16-second delay

                    self.calib_delay_timer = QTimer()
                    self.calib_delay_timer.setSingleShot(True)
                    self.calib_delay_timer.timeout.connect(lambda: self.arduino.send_command('D'))
                    self.calib_delay_timer.start(21000)  # 5-second delay

                    # self.webcam_focus_delay = QTimer()
                    # self.webcam_focus_delay.setSingleShot(True)
                    # self.webcam_focus_delay.timeout.connect(lambda: playsound('Sound/waitToFocus.mp3'))
                    # self.webcam_focus_delay.start(41000)  # 20-second delay, wait for accessing calibration mode.

                    # self.preopen_air_delay = QTimer()
                    # self.preopen_air_delay.setSingleShot(True)
                    # self.preopen_air_delay.timeout.connect(lambda: playsound('Sound/openAir.mp3'))
                    # self.preopen_air_delay.start(46000)  # 5-second delay, wait for webcam.

                    self.opening_air_delay = QTimer()
                    self.opening_air_delay.setSingleShot(True)
                    self.opening_air_delay.timeout.connect(lambda: self.arduino.send_command('I'))
                    self.opening_air_delay.start(50000-10000)  # 4-second delay, wait for opening air.

                    # self.while_opening_air_delay = QTimer()
                    # self.while_opening_air_delay.setSingleShot(True)
                    # self.while_opening_air_delay.timeout.connect(lambda: playsound('Sound/waitForPressure.mp3'))
                    # self.while_opening_air_delay.start(60000)  # 10-second delay, wait for pressue balancing.

                    # self.closing_air_delay = QTimer()
                    # self.closing_air_delay.setSingleShot(True)
                    # self.closing_air_delay.timeout.connect(lambda: playsound('Sound/closeAir.mp3'))
                    # self.closing_air_delay.start(65000)  # 10-second delay, wait for closing air.

                    self.after_closing_air_delay = QTimer()
                    self.after_closing_air_delay.setSingleShot(True)
                    self.after_closing_air_delay.timeout.connect(lambda: self.arduino.send_command('H'))                   
                    self.after_closing_air_delay.start(69000-10000)  # 4-second delay, wait for closing air sound then close air. 

                    # self.preopening_middle_valve_delay = QTimer()
                    # self.preopening_middle_valve_delay.setSingleShot(True)
                    # self.preopening_middle_valve_delay.timeout.connect(lambda: playsound('Sound/middleValveOpen.mp3'))
                    # self.preopening_middle_valve_delay.start(71000)  # 4-second delay, wait for closing air. 

                    self.opening_middle_valve_delay = QTimer()
                    self.opening_middle_valve_delay.setSingleShot(True)
                    self.opening_middle_valve_delay.timeout.connect(lambda: self.arduino.send_command('F'))
                    self.opening_middle_valve_delay.start(73000-10000)  # 2-second delay, wait for openning mid air to reduce pressure to 0.

                    self.post_opening_middle_valve_delay = QTimer()
                    self.post_opening_middle_valve_delay.setSingleShot(True)
                    self.post_opening_middle_valve_delay.timeout.connect(lambda: self.arduino.send_command('J'))
                    self.post_opening_middle_valve_delay.start(77000-10000)  # 4-second delay, wait for openning mid air to reduce pressure to 0 and then close air.

                    self.presnapshot_delay = QTimer()
                    self.presnapshot_delay.setSingleShot(True)
                    self.presnapshot_delay.timeout.connect(self.closeButton.click)
                    self.presnapshot_delay.start(78000-10000)

                    self.pre2snapshot_delay = QTimer()
                    self.pre2snapshot_delay.setSingleShot(True)
                    self.pre2snapshot_delay.timeout.connect(self.viewButton.click)
                    self.pre2snapshot_delay.start(80000-10000)

                    self.snapshot_delay = QTimer()
                    self.snapshot_delay.setSingleShot(True)
                    self.snapshot_delay.timeout.connect(self.stopButton.click)
                    self.snapshot_delay.start(82000-10000) # 4-second delay, wait for openning mid air to reduce pressure to 0 and then close air.


                elif extracted_text.strip() == "UNLOCKED":
                    # playsound('Sound/UnlockedMode.mp3')
                    # Implement further logic for unlocked mode
                    self.arduino.send_command('K')  # Retract actuators 2 and 3
                # Introduce a 5-second delay before calling afterDelayToCalib
                    # self.calib_delay_timer = QTimer()
                    # self.calib_delay_timer.setSingleShot(True)
                    # self.calib_delay_timer.timeout.connect(self.afterDelayToCalib)
                    # self.calib_delay_timer.start(5000)  # 5-second delay
                else: 
                    return
            else: 
                QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Webcam is not opening")





    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Automated Calibration System GUI"))
        self.kpaLabel.setText(_translate("MainWindow", "Kpa"))
        self.exitButton.setText(_translate("MainWindow", "Exit"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.calLabel.setText(_translate("MainWindow", "Cal"))
        self.resetButton.setText(_translate("MainWindow", "Reset"))
        self.stopButton.setText(_translate("MainWindow", "Estop"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Control GUI"))
        self.viewButton.setText(_translate("MainWindow", "View"))
        self.closeButton.setText(_translate("MainWindow", "Close"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Webcam"))
        self.menuMain_layout.setTitle(_translate("MainWindow", "Main GUI"))

    def startWebcam(self):
        # Set up timer for updating the frame
        if not self.is_webcam_open_first_time:
            for _ in range(2):
                self.cap = cv2.VideoCapture(2)
            self.is_webcam_open_first_time = True
            
        else: 
            self.cap = cv2.VideoCapture(2)

        if self.cap.isOpened():
            self.is_webcam_open = True  # Webcam is successfully opened
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)  # Update frame every 30 ms
        else:
            # Handle error if webcam couldn't be opened
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Could not open webcam. Click View button again.")
            return  # Exit the method if webcam is not opened


    def stop_webcam(self):
        self.timer.stop()
        self.cap.release()

    def exitWindow(self):
        MainWindow.close()


    def resetWindow(self):
        self.arduino.send_command('G')
        self.stop_webcam()

        QtWidgets.QApplication.closeAllWindows()  # Closes the current active window
        self.new_window = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.new_window)
        self.new_window.showNormal()        

    def confirmExit(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
        font = QtGui.QFont()
        font.setPointSize(20)  # Set a larger font size
        msgBox.setFont(font)
        msgBox.setStyleSheet(""" QMessageBox {
                                    min-width: 400px;  /* Set the minimum width */
                                    min-height: 200px;  /* Set the minimum height */
                                }
                                QPushButton {
                                    font-size: 14px;  /* Increase font size of buttons */
                                    padding: 10px;     /* Add padding to make buttons larger */
                                }
                                QLabel {
                                    font-size: 16px;  /* Increase font size of the label text */
                                }""")
        msgBox.setWindowTitle('Confirm Exit')
        msgBox.setText('Are you sure you want to exit?')



        
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.No)

        response = msgBox.exec_()

        if response == QtWidgets.QMessageBox.Yes:
            QtWidgets.QApplication.quit()

    def confirmStart(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
        font = QtGui.QFont()
        font.setPointSize(20)  # Set a larger font size
        msgBox.setFont(font)
        msgBox.setStyleSheet(""" QMessageBox {
                                    min-width: 400px;  /* Set the minimum width */
                                    min-height: 200px;  /* Set the minimum height */
                                }
                                QPushButton {
                                    font-size: 14px;  /* Increase font size of buttons */
                                    padding: 10px;     /* Add padding to make buttons larger */
                                }
                                QLabel {
                                    font-size: 16px;  /* Increase font size of the label text */
                                }""")
        msgBox.setWindowTitle('Confirm Start')
        msgBox.setText('Are you sure you want to start?')



        
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.No)

        response = msgBox.exec_()

        if response == QtWidgets.QMessageBox.Yes:
            self.start()        


    def confirmReset(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
        font = QtGui.QFont()
        font.setPointSize(20)  # Set a larger font size
        msgBox.setFont(font)
        msgBox.setStyleSheet(""" QMessageBox {
                                    min-width: 400px;  /* Set the minimum width */
                                    min-height: 200px;  /* Set the minimum height */
                                }
                                QPushButton {
                                    font-size: 14px;  /* Increase font size of buttons */
                                    padding: 10px;     /* Add padding to make buttons larger */
                                }
                                QLabel {
                                    font-size: 16px;  /* Increase font size of the label text */
                                }""")
        msgBox.setWindowTitle('Confirm Reset')
        msgBox.setText('Are you sure you want to restart?')



        
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.No)

        response = msgBox.exec_()

        if response == QtWidgets.QMessageBox.Yes:
            self.resetWindow()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:      
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            qt_pixmap = QPixmap.fromImage(qt_image)
            self.webcamFrame.setPixmap(qt_pixmap)
            # self.webcam_label.setScaledContents(True)
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
        rect_width = 470 
        rect_height = 120 
        rect_x = 80
        rect_y = 160
        
        # Draw the hollow rectangle
        painter.drawRect(rect_x, rect_y, rect_width, rect_height)
        
        # End painting
        painter.end()
        
        # Update the label with the modified pixmap
        self.webcamFrame.setPixmap(pixmap)

    def snapshot(self):
        # self.stop_webcam()
        # self.startWebcam()
        ret, frame = self.cap.read()
        if ret:
            # Calculate the size and position for the rectangle (same as in draw_red_rectangle)
            rect_width = 470 #latest version of the dimension 
            rect_height = 120 
            rect_x = 100
            rect_y = 160

            # Crop the frame to the size of the red rectangle
            cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"SnapShotImages/processed_snapshot_simple{timestamp}.jpg"         
            # Save the processed image for OCR
            cv2.imwrite(image_filename, cropped_frame)

            # Perform OCR on the cropped image
            img_with_text, extracted_text = self.ocr_processor.run_ocr(image_filename)
            result = self.ocr_processor.run_ocr_simple(image_filename)
            print(result)

            combined_string = ' '.join(result)

            print(combined_string)
            part1, part2, part3, part4 = combined_string.split()
            print(part1)
            

            print(part2)
            resultKpa = int(part2)
            print(resultKpa)
            self.kpaLCDNumber.display(resultKpa)

            resultCal = int(part4)
            print(resultCal)
            self.calLCDNumber.display(resultCal)

            if (resultKpa == 0):
                self.arduino.send_command('O') #Green LED on 
            else: 
                self.arduino.send_command('M') #Red LED on 





if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.showNormal()
    sys.exit(app.exec_())
