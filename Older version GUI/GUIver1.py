# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GUIver1.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter

from ocr import OCRProcessor
from datetime import datetime
from utils import SerialCommunicator
import serial.tools.list_ports
import time 
from playsound import playsound
import cv2

class TextWindow(QtWidgets.QWidget):
    def __init__(self, file_path):
        super().__init__()
        self.initUI(file_path)

    def initUI(self, file_path):
        self.setWindowTitle('Text File Viewer')
        self.setGeometry(200, 200, 800, 600)
        
        # Create a QTextEdit to display the text
        self.textEdit = QtWidgets.QTextEdit(self)
        self.textEdit.setGeometry(10, 10, 780, 580)

        # Load the text file content
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                self.textEdit.setText(content)  # Set the file content to the QTextEdit
        except FileNotFoundError:
            self.textEdit.setText("File not found!")

        self.show()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 750)
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
        self.webcamFrame = QtWidgets.QLabel(self.centralwidget)
        self.webcamFrame.setGeometry(QtCore.QRect(220, 10, 591, 501))
        self.webcamFrame.setMouseTracking(False)
        self.webcamFrame.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.webcamFrame.setFrameShape(QtWidgets.QFrame.Box)
        self.webcamFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.webcamFrame.setLineWidth(2)
        self.webcamFrame.setMidLineWidth(0)
        self.webcamFrame.setText("")
        self.webcamFrame.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.webcamFrame.setObjectName("webcamFrame")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(0, 10, 211, 371))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.startButton.setFont(font)
        self.startButton.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.startButton.setAutoFillBackground(False)
        self.startButton.setStyleSheet("background-color: rgb(138, 226, 52);")
        self.startButton.setObjectName("startButton")
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setGeometry(QtCore.QRect(820, 10, 171, 491))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.stopButton.setFont(font)
        self.stopButton.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.stopButton.setAutoFillBackground(False)
        self.stopButton.setStyleSheet("background-color: rgb(204, 0, 0);")
        self.stopButton.setObjectName("stopButton")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(220, 520, 591, 71))
        self.progressBar.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.progressBar.setProperty("value", 0)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.logFileButton = QtWidgets.QPushButton(self.centralwidget)
        self.logFileButton.setGeometry(QtCore.QRect(820, 520, 171, 71))
        self.logFileButton.setStyleSheet("background-color: rgb(252, 175, 62);")
        self.logFileButton.setObjectName("logFileButton")
        self.systemStatus = QtWidgets.QLabel(self.centralwidget)
        self.systemStatus.setGeometry(QtCore.QRect(10, 400, 201, 51))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(15)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.systemStatus.setFont(font)
        self.systemStatus.setObjectName("systemStatus")
        self.mainValveStatus = QtWidgets.QLabel(self.centralwidget)
        self.mainValveStatus.setGeometry(QtCore.QRect(10, 460, 201, 51))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(15)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.mainValveStatus.setFont(font)
        self.mainValveStatus.setObjectName("mainValveStatus")
        self.mainValveLED = QtWidgets.QLabel(self.centralwidget)
        self.mainValveLED.setGeometry(QtCore.QRect(170, 470, 31, 31))
        self.mainValveLED.setStyleSheet("background-color: rgb(138, 226, 52);")
        self.mainValveLED.setText("")
        self.mainValveLED.setObjectName("mainValveLED")
        self.midValveStatus = QtWidgets.QLabel(self.centralwidget)
        self.midValveStatus.setGeometry(QtCore.QRect(10, 520, 201, 51))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(15)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.midValveStatus.setFont(font)
        self.midValveStatus.setObjectName("midValveStatus")
        self.midValveLED = QtWidgets.QLabel(self.centralwidget)
        self.midValveLED.setGeometry(QtCore.QRect(170, 530, 31, 31))
        self.midValveLED.setStyleSheet("background-color: rgb(138, 226, 52);")
        self.midValveLED.setText("")
        self.midValveLED.setObjectName("midValveLED")
        self.calLCDNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.calLCDNumber.setGeometry(QtCore.QRect(620, 600, 191, 81))
        self.calLCDNumber.setStyleSheet("background-color: rgb(252, 233, 79);")
        self.calLCDNumber.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.calLCDNumber.setProperty("intValue", 0)
        self.calLCDNumber.setObjectName("calLCDNumber")
        self.calLabel = QtWidgets.QLabel(self.centralwidget)
        self.calLabel.setGeometry(QtCore.QRect(530, 600, 91, 81))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.calLabel.setFont(font)
        self.calLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.calLabel.setObjectName("calLabel")
        self.kpaLCDNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.kpaLCDNumber.setGeometry(QtCore.QRect(310, 600, 211, 81))
        self.kpaLCDNumber.setStyleSheet("background-color: rgb(252, 233, 79);")
        self.kpaLCDNumber.setSmallDecimalPoint(False)
        self.kpaLCDNumber.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.kpaLCDNumber.setProperty("value", 0.0)
        self.kpaLCDNumber.setProperty("intValue", 0)
        self.kpaLCDNumber.setObjectName("kpaLCDNumber")
        self.kpaLabel = QtWidgets.QLabel(self.centralwidget)
        self.kpaLabel.setGeometry(QtCore.QRect(220, 600, 91, 81))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(25)
        font.setBold(True)
        font.setWeight(75)
        self.kpaLabel.setFont(font)
        self.kpaLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.kpaLabel.setObjectName("kpaLabel")
        self.textBox = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBox.setGeometry(QtCore.QRect(220, 960, 1001, 81))
        self.textBox.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.textBox.setObjectName("textBox")
        self.systemLED = QtWidgets.QLabel(self.centralwidget)
        self.systemLED.setGeometry(QtCore.QRect(170, 410, 31, 31))
        self.systemLED.setStyleSheet("background-color: rgb(138, 226, 52);")
        self.systemLED.setText("")
        self.systemLED.setObjectName("systemLED")
        self.captureAnDetectButton = QtWidgets.QPushButton(self.centralwidget)
        self.captureAnDetectButton.setGeometry(QtCore.QRect(10, 600, 201, 81))
        self.captureAnDetectButton.setStyleSheet("background-color: rgb(252, 175, 62);")
        self.captureAnDetectButton.setObjectName("captureAnDetectButton")

        self.resetButton = QtWidgets.QPushButton(self.centralwidget)
        self.resetButton.setGeometry(QtCore.QRect(820, 600, 171, 81))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.resetButton.setFont(font)
        self.resetButton.setStyleSheet("background-color: rgb(252, 175, 62);")
        self.resetButton.setObjectName("resetButton")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 26))
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
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Initialize Webcam Capture
        self.cap = cv2.VideoCapture(0)

        # Set up timer for updating the frame
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update frame every 30 ms

        # Connect start and stop buttons
        self.startButton.clicked.connect(self.startCalibrate)
        self.captureAnDetectButton.clicked.connect(self.captureAndDetect)
        self.stopButton.clicked.connect(self.stop_webcam)
        self.resetButton.clicked.connect(self.restartApp)
        self.logFileButton.clicked.connect(self.openTextFile)
        # self.arduino = SerialCommunicator(port='/dev/ttyUSB1', baudrate=115200, timeout=1)

        self.ocr_processor = OCRProcessor()


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Automated Calibration System GUI"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.stopButton.setText(_translate("MainWindow", "Estop"))
        self.logFileButton.setText(_translate("MainWindow", "Open log file"))
        self.systemStatus.setText(_translate("MainWindow", "System "))
        self.mainValveStatus.setText(_translate("MainWindow", "Main valve"))
        self.midValveStatus.setText(_translate("MainWindow", "Mid valve"))
        self.calLabel.setText(_translate("MainWindow", "Cal"))
        self.kpaLabel.setText(_translate("MainWindow", "Kpa"))
        self.captureAnDetectButton.setText(_translate("MainWindow", "Capture and detect"))
        self.resetButton.setText(_translate("MainWindow", "Reset"))
        self.menuMain_layout.setTitle(_translate("MainWindow", "Main layout"))

    def captureAndDetect(self):
        ret, frame = self.cap.read()
        if ret:
            # Calculate the size and position for the rectangle (same as in draw_red_rectangle)
            rect_width = 550 
            rect_height = 130 
            rect_x = 100
            rect_y = 150

            # Crop the frame to the size of the red rectangle
            cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"SnapShotImages/processed_snapshot{timestamp}.jpg"         
            # Save the processed image for OCR
            cv2.imwrite(image_filename, cropped_frame)

            # Perform OCR on the cropped image
            img_with_text, extracted_text = self.ocr_processor.run_ocr('SnapShotImages/processed_snapshot20240919_180259.jpg')
            result = self.ocr_processor.run_ocr_simple('SnapShotImages/processed_snapshot20240919_180259.jpg')
            print(result[1]) #Kpa 
            result_int_Kpa = int(result[1])
            print(result_int_Kpa)
            print(result[3]) #Cal 
            result_int_Cal = int(result[3])
            print(result_int_Cal)


            #Display to the LCD
            self.calLCDNumber.display(result_int_Cal)
            self.kpaLCDNumber.display(result_int_Kpa)

            # Convert the processed image to QImage
            h, w, ch = img_with_text.shape
            bytes_per_line = ch * w
            qt_image = QImage(img_with_text.data, w, h, bytes_per_line, QImage.Format_RGB888)
            qt_pixmap = QPixmap.fromImage(qt_image)
            
            # Display the processed image in the captured_label
            self.webcamFrame.setPixmap(qt_pixmap)
            self.webcamFrame.setAlignment(Qt.AlignCenter)
            self.progressBar.setValue(100)
            self.timer.stop()
            self.cap.release() 
        return result_int_Kpa, result_int_Cal
    
    def startCalibrate(self):

        self.systemLED.setStyleSheet("background-color: rgb(255, 0, 0);") #LED sytem: red

        self.progressBar.setValue(0)

        # self.arduino.send_command('A')  # Extend the actuator 2 and 3 and pump ON
        command2check = "L"  # Check command from arduino
        # response = self.arduino.read_command()
        response = "L"
        print(response)

        # Timer for after_delay execution
        self.delay_timer = QTimer()
        self.delay_timer.setSingleShot(True)  # Make sure the timer fires only once
        self.delay_timer.timeout.connect(lambda: self.afterDelay(response, command2check))
        self.delay_timer.start(5000)  # 5-second delay before calling after_delay




    def afterDelay(self, response, command2check):
        if response == command2check:

            ret, frame = self.cap.read()
            if ret:
                # Process and crop the frame for OCR
                rect_width = 550
                rect_height = 130
                rect_x = 100
                rect_y = 150
                cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]


                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"SnapShotImages/processed_snapshot_LOCK2UNLOCK{timestamp}.jpg"

                # Save the processed image for OCR
                cv2.imwrite(image_filename, cropped_frame)

                # Perform OCR on the cropped image
                img_with_text, extracted_text = self.ocr_processor.run_ocr('SnapShotImages/processed_snapshot_LOCK2UNLOCK20240919_180834.jpg')

                self.progressBar.setValue(20)

                # Perform further actions based on OCR result
                if extracted_text.strip() == "LOCKED":

                    playsound('Sound/LockedModeVer2.mp3')

                    self.stop_timer = QTimer()
                    self.stop_timer.setSingleShot(True)
                    # self.stop_timer.timeout.connect(lambda: self.arduino.send_command('K'))
                    self.stop_timer.timeout.connect(lambda: print('K'))
                    self.stop_timer.start(3000)  # 3-second delay before retracting actuator 2 and 3

                    # Timer for second action: retract_button_2.click() (Turn off the pump controller)
                    self.retract_timer = QTimer()
                    self.retract_timer.setSingleShot(True)
                    # self.retract_timer.timeout.connect(lambda: self.arduino.send_command('C')) #Controller off
                    self.retract_timer.timeout.connect(lambda: print('C'))
                    self.retract_timer.start(6000)  # 6-second delay

                    # Timer for third action: send_command('R') to extend actuators 2 and 3
                    self.command_timer = QTimer()
                    self.command_timer.setSingleShot(True)
                    # self.command_timer.timeout.connect(lambda: self.arduino.send_command('R')) #Extend Act2 and Act3
                    self.command_timer.timeout.connect(lambda: print('R'))
                    self.command_timer.start(9000)  # 9-second delay

                    # Timer for fourth action: Turn off the controller
                    self.pumpOn_timer = QTimer()
                    self.pumpOn_timer.setSingleShot(True)
                    # self.pumpOn_timer.timeout.connect(lambda: self.arduino.send_command('B')) #Controller on
                    self.pumpOn_timer.timeout.connect(lambda: print('B'))
                    self.pumpOn_timer.start(12000)  # 12-second delay


                    # self.progressBar.setValue(40)

                    # Timer for retracting actuator 2 and 3 again
                    self.retract_time_2 = QTimer()
                    self.retract_time_2.setSingleShot(True)
                    # self.retract_time_2.timeout.connect(lambda: self.arduino.send_command('K')) #Retract Act2 and Act3
                    self.retract_time_2.timeout.connect(lambda: print('K'))
                    self.retract_time_2.start(16000)  # 16-second delay

                    self.calib_delay_timer = QTimer()
                    self.calib_delay_timer.setSingleShot(True)
                    # self.calib_delay_timer.timeout.connect(self.afterDelayToCalib)
                    self.calib_delay_timer.timeout.connect(lambda: print('AfterDelayToCalib'))
                    self.calib_delay_timer.start(21000)  # 5-second delay

                    self.webcam_focus_delay = QTimer()
                    self.webcam_focus_delay.setSingleShot(True)
                    self.webcam_focus_delay.timeout.connect(lambda: playsound('Sound/waitToFocus.mp3'))
                    self.webcam_focus_delay.start(41000)  # 20-second delay, wait for accessing calibration mode.

                    # self.progressBar.setValue(50)

                    self.preopen_air_delay = QTimer()
                    self.preopen_air_delay.setSingleShot(True)
                    self.preopen_air_delay.timeout.connect(lambda: playsound('Sound/openAir.mp3'))
                    self.preopen_air_delay.start(46000)  # 5-second delay, wait for webcam.


                    self.opening_air_delay = QTimer()
                    self.opening_air_delay.setSingleShot(True)
                    # self.opening_air_delay.timeout.connect(lambda:self.openAir) #Open air
                    self.opening_air_delay.timeout.connect(lambda: print('I'))
                    self.opening_air_delay.start(50000)  # 4-second delay, wait for opening air.

                    self.while_opening_air_delay = QTimer()
                    self.while_opening_air_delay.setSingleShot(True)
                    self.while_opening_air_delay.timeout.connect(lambda: playsound('Sound/waitForPressure.mp3'))
                    self.while_opening_air_delay.start(60000)  # 10-second delay, wait for pressue balancing.

                    self.closing_air_delay = QTimer()
                    self.closing_air_delay.setSingleShot(True)
                    self.closing_air_delay.timeout.connect(lambda: playsound('Sound/closeAir.mp3'))
                    self.closing_air_delay.start(65000)  # 10-second delay, wait for closing air.

                    self.after_closing_air_delay = QTimer()
                    self.after_closing_air_delay.setSingleShot(True)
                    # self.after_closing_air_delay.timeout.connect(lambda: self.closeAir)
                    self.after_closing_air_delay.timeout.connect(lambda: print('H'))
                    self.after_closing_air_delay.start(69000)  # 4-second delay, wait for closing air sound then close air. 

                    self.preopening_middle_valve_delay = QTimer()
                    self.preopening_middle_valve_delay.setSingleShot(True)
                    self.preopening_middle_valve_delay.timeout.connect(lambda: playsound('Sound/middleValveOpen.mp3'))
                    self.preopening_middle_valve_delay.start(71000)  # 4-second delay, wait for closing air. 

                    self.opening_middle_valve_delay = QTimer()
                    self.opening_middle_valve_delay.setSingleShot(True)
                    # self.opening_middle_valve_delay.timeout.connect(lambda: self.midValveOpenAir)
                    self.opening_middle_valve_delay.timeout.connect(lambda: print('F'))
                    self.opening_middle_valve_delay.start(73000)  # 2-second delay, wait for openning mid air to reduce pressure to 0.

                    self.post_opening_middle_valve_delay = QTimer()
                    self.post_opening_middle_valve_delay.setSingleShot(True)
                    # self.post_opening_middle_valve_delay.timeout.connect(lambda: self.midValveCloseAir)
                    self.post_opening_middle_valve_delay.timeout.connect(lambda: print('J'))
                    self.post_opening_middle_valve_delay.start(77000)  # 4-second delay, wait for openning mid air to reduce pressure to 0 and then close air.
                    
                    # Timer for after_delay execution
                    self.readKpaAndCal_timer = QTimer()
                    self.readKpaAndCal_timer.setSingleShot(True)  # Make sure the timer fires only once
                    self.readKpaAndCal_timer.timeout.connect(self.captureAnDetectButton.click)
                    self.readKpaAndCal_timer.start(78000)  # 5-second delay before calling after_delay
            
 
                elif extracted_text.strip() == "UNLOCKED":
                    self.status_label.setText('UNLOCKED MODE')
                    playsound('Sound/UnlockedMode.mp3')
                    # Implement further logic for unlocked mode
                    self.arduino.send_command('K')  # Retract actuators 2 and 3
                # Introduce a 5-second delay before calling afterDelayToCalib
                    self.calib_delay_timer = QTimer()
                    self.calib_delay_timer.setSingleShot(True)
                    self.calib_delay_timer.timeout.connect(self.afterDelayToCalib)
                    self.calib_delay_timer.start(5000)  # 5-second delay


            

    def afterDelayToCalib(self):
        # Extend actuator 2 and 4
        self.arduino.send_command('D')

        # Timer for playing calibration sound
        self.delay_timer_arduino_to_calib = QTimer()
        self.delay_timer_arduino_to_calib.setSingleShot(True)
        self.delay_timer_arduino_to_calib.timeout.connect(lambda: playsound('Sound/calibration_mode.mp3'))
        self.delay_timer_arduino_to_calib.start(16000)  # 16-second delay



    def stop_webcam(self):
        result = self.captureAndDetect()
        print(result)

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

    def openAir(self):
        self.mainValveLED.setStyleSheet("background-color: rgb(255, 0, 0);") #LED main valve: red
        self.arduino.send_command('I')

    def closeAir(self):
        self.mainValveLED.setStyleSheet("background-color: rgb(0, 255, 0);") #LED main valve: green
        self.arduino.send_command('H')

    def midValveOpenAir(self):
        self.midValveLED.setStyleSheet("background-color: rgb(255, 0, 0);") #LED mid valve: red
        self.arduino.send_command('F')

    def midValveCloseAir(self):
        self.midValveLED.setStyleSheet("background-color: rgb(0, 255, 0);") #LED mid valve: green
        self.arduino.send_command('J')

    def readKpaAndCal(self):
        result = self.captureAndDetect()
        print(result)

    def restartApp(self):
        # Close the current window
        MainWindow.close()

        # Reopen a new instance of the main window
        self.reopenMainWindow()

    def reopenMainWindow(self):

        # Create a new instance of MainWindow and reopen the UI

        self.new_window = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.new_window)
        self.new_window.show()

    def openTextFile(self):
        # Define the path to the text file
        file_path = "log.txt"  # Replace this with the path to your text file
        
        # Open the new window and display the text file content
        self.text_window = TextWindow(file_path)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
