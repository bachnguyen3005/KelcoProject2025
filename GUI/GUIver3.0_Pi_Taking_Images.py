from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QImage, QPixmap, QPainter, QMovie
import serial
from ocr import OCRProcessor
from utils import SerialCommunicator
import cv2
from datetime import datetime
import time

    
class LoadingSplashScreen(QtWidgets.QSplashScreen):
    def __init__(self, gif_path):
        super().__init__()
        
        # Create label to display the GIF
        self.label = QtWidgets.QLabel(self)
        self.movie = QMovie('/home/billy/GUI/1488.gif')
        self.label.setMovie(self.movie)
        
        # Center the label on the splash screen
        self.setFixedSize(250, 250)
        self.label.setGeometry(0, 0, 250, 250)
        self.movie.start()

    def stop_animation(self):
        self.movie.stop()
        self.close()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 480)
        MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        MainWindow.setMouseTracking(False)
        #icon = QtGui.QIcon()
        #icon.addPixmap(QtGui.QPixmap("../../../../../../../Documents/PlatformIO/Projects/kelco_test_001/beta.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        #MainWindow.setWindowIcon(icon)
        MainWindow.setWindowOpacity(1.0)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("background-color: rgb(114, 159, 207);")
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
        font = QtGui.QFont()
        font.setFamily("Sans")
        font.setItalic(True)
        self.tabWidget.setFont(font)
        self.tabWidget.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.tabWidget.setStyleSheet("background-color: rgb(114, 159, 207);")
        self.tabWidget.setObjectName("tabWidget")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.scrollArea = QtWidgets.QScrollArea(self.tab_3)
        self.scrollArea.setStyleSheet("background-color: rgb(114, 159, 207);")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 650, 270))
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
        self.kpaLabel.setFrameShadow(QtWidgets.QFrame.Plain)
        self.kpaLabel.setLineWidth(2)
        self.kpaLabel.setScaledContents(False)
        self.kpaLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.kpaLabel.setObjectName("kpaLabel")
        self.gridLayout_2.addWidget(self.kpaLabel, 6, 0, 1, 1)
        self.calLCDNumber = QtWidgets.QLCDNumber(self.scrollAreaWidgetContents)
        self.calLCDNumber.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.calLCDNumber.setStyleSheet("background-color: rgba(255, 249, 0, 236);\n"
"color: rgb(0, 38, 255);")
        self.calLCDNumber.setFrameShape(QtWidgets.QFrame.Box)
        self.calLCDNumber.setFrameShadow(QtWidgets.QFrame.Plain)
        self.calLCDNumber.setLineWidth(1)
        self.calLCDNumber.setSmallDecimalPoint(False)
        self.calLCDNumber.setMode(QtWidgets.QLCDNumber.Dec)
        self.calLCDNumber.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.calLCDNumber.setProperty("intValue", 0)
        self.calLCDNumber.setObjectName("calLCDNumber")
        self.gridLayout_2.addWidget(self.calLCDNumber, 7, 1, 1, 2) # Change to 7, 1, 1, 2 as wrong placement with kPaLCDNumber location
        self.startButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(30)
        self.startButton.setFont(font)
        self.startButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.startButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.startButton.setAutoFillBackground(False)
        self.startButton.setStyleSheet("background-color: rgb(0, 255, 0);")
        self.startButton.setDefault(True)
        self.startButton.setFlat(False)
        self.startButton.setObjectName("startButton")
        self.gridLayout_2.addWidget(self.startButton, 1, 0, 1, 3)
        self.calLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(40)
        font.setBold(True)
        font.setWeight(75)
        self.calLabel.setFont(font)
        self.calLabel.setStyleSheet("background-color: rgb(252, 233, 79);")
        self.calLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.calLabel.setFrameShadow(QtWidgets.QFrame.Plain)
        self.calLabel.setLineWidth(2)
        self.calLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.calLabel.setObjectName("calLabel")
        self.gridLayout_2.addWidget(self.calLabel, 7, 0, 1, 1)
        self.kpaLCDNumber = QtWidgets.QLCDNumber(self.scrollAreaWidgetContents)
        self.kpaLCDNumber.setStyleSheet("background-color: rgba(255, 249, 0, 236);\n"
"color: rgb(0, 38, 255);")
        self.kpaLCDNumber.setFrameShape(QtWidgets.QFrame.Box)
        self.kpaLCDNumber.setFrameShadow(QtWidgets.QFrame.Plain)
        self.kpaLCDNumber.setMidLineWidth(0)
        self.kpaLCDNumber.setSmallDecimalPoint(False)
        self.kpaLCDNumber.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.kpaLCDNumber.setProperty("value", 0.0)
        self.kpaLCDNumber.setProperty("intValue", 0)
        self.kpaLCDNumber.setObjectName("kpaLCDNumber")
        self.gridLayout_2.addWidget(self.kpaLCDNumber, 6, 1, 1, 2) # Change to 6, 1, 1, 2 as wrong placement with calLCDNumber location
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_3.addWidget(self.scrollArea, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab_4)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.scrollArea_2 = QtWidgets.QScrollArea(self.tab_4)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName("scrollArea_2")
        self.scrollAreaWidgetContents_2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 650, 270))
        self.scrollAreaWidgetContents_2.setObjectName("scrollAreaWidgetContents_2")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents_2)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.webcamFrame = QtWidgets.QLabel(self.scrollAreaWidgetContents_2)
        self.webcamFrame.setText("")
        self.webcamFrame.setObjectName("webcamFrame")
        self.gridLayout_5.addWidget(self.webcamFrame, 0, 0, 1, 2)
        self.closeButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents_2)
        self.closeButton.setStyleSheet("background-color: rgb(239, 41, 41);")
        self.closeButton.setDefault(True)
        self.closeButton.setObjectName("closeButton")
        self.gridLayout_5.addWidget(self.closeButton, 3, 1, 1, 1)
        self.viewButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents_2)
        self.viewButton.setStyleSheet("background-color: rgb(173, 127, 168);")
        self.viewButton.setDefault(True)
        self.viewButton.setObjectName("viewButton")
        self.gridLayout_5.addWidget(self.viewButton, 3, 0, 1, 1)
        self.Snap = QtWidgets.QPushButton(self.scrollAreaWidgetContents_2)
        self.Snap.setObjectName("Snap")
        self.gridLayout_5.addWidget(self.Snap, 3, 2, 1, 1)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.gridLayout_4.addWidget(self.scrollArea_2, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_4, "")
        self.gridLayout.addWidget(self.tabWidget, 2, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 700, 26))
        self.menubar.setStyleSheet("")
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.is_webcam_open = False
        
        self.is_webcam_open_first_time = False

        self.is_running = False  # Track the current state (GO/STOP)

        self.timers = []  # List to store all the timers

        self.arduino = SerialCommunicator(port='/dev/ttyUSB0', baudrate=115200, timeout=1)

        self.viewButton.clicked.connect(self.startWebcam)

        self.closeButton.clicked.connect(self.stop_webcam)

        self.startButton.clicked.connect(self.toggleGoStop)

        self.Snap.clicked.connect(self.snapshot)
        
        #self.max_try = 0 #Use for maximum try when calibrate

        QTimer.singleShot(0, self.initialize_ocr)
        QTimer.singleShot(0, self.startWebcam)

        
    def initialize_ocr(self):
        self.ocr_processor = OCRProcessor()
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Automated Calibration System GUI"))
        self.kpaLabel.setText(_translate("MainWindow", "kPa"))
        self.startButton.setText(_translate("MainWindow", "GO"))
        self.calLabel.setText(_translate("MainWindow", "Cal"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Control GUI"))
        self.closeButton.setText(_translate("MainWindow", "Close"))
        self.viewButton.setText(_translate("MainWindow", "View"))
        self.Snap.setText(_translate("MainWindow", "Snap"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "Webcam"))
        
    def toggleGoStop(self):
        if not self.is_running:
            # Start the process
            self.confirmStart()
        else:
            # Stop the process
            self.confirmStop()
            if self.is_confirmStop_Yes:
                self.startButton.setText("GO")
                self.startButton.setStyleSheet("background-color: rgb(138, 226, 52);")
                self.is_running = False
            elif self.is_confirmStop_Yes == False:
                return


    def start(self):
        self.calLCDNumber.display(0) # Reset the value to 0
        self.kpaLCDNumber.display(0) # Reset the value to 0
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
            self.timers.append(self.delay_timer)
        else:
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Could not open webcam. Click View button again.")
            return
        
    def stop(self):
        # Stop all timers when STOP button is pressed
        for timer in self.timers:
            if timer.isActive():
                timer.stop()
        self.timers.clear()  # Clear the timers list

        self.arduino.send_command('G') # Stop all

    def after_delay(self, response, command2check):
        if response == command2check:

            ret, frame = self.cap.read()
            if ret:
                # Process and crop the frame for OCR
                rect_width = 500 
                rect_height = 140 
                rect_x = 70
                rect_y = 150
                cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width] # Crop LCD image 


                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") # Save the cropped image 
                image_filename = f"/home/billy/GUI/SnapShotImages/processed_snapshot_LOCK2UNLOCK{timestamp}.jpg"

                # Save the processed image for OCR
                cv2.imwrite(image_filename, cropped_frame)

                # Perform OCR on the cropped image
                extracted_text = self.ocr_processor.get_lock_status(image_filename)
                print(extracted_text)

                # Perform further actions based on OCR result
                if extracted_text == "LOCKED":
                    
                    self.stop_timer = QTimer()
                    self.stop_timer.setSingleShot(True)
                    self.stop_timer.timeout.connect(lambda: self.arduino.send_command('K'))
                    self.stop_timer.start(3000)  # 3-second delay before retracting actuator 2 and 3
                    self.timers.append(self.stop_timer)

                    # Timer for second action: retract_button_2.click() (Turn off the pump controller)
                    self.retract_timer = QTimer()
                    self.retract_timer.setSingleShot(True)
                    self.retract_timer.timeout.connect(lambda: self.arduino.send_command('C')) #Pump off
                    self.retract_timer.start(6000)  # 6-second delay
                    self.timers.append(self.retract_timer)

                    # Timer for third action: send_command('R') to extend actuators 2 and 3
                    self.command_timer = QTimer()
                    self.command_timer.setSingleShot(True)
                    self.command_timer.timeout.connect(lambda: self.arduino.send_command('R')) #Extend Act2 and Act3
                    self.command_timer.start(9000)  # 9-second delay
                    self.timers.append(self.command_timer)

                    # Timer for fourth action: Turn off the controller
                    self.pumpOn_timer = QTimer()
                    self.pumpOn_timer.setSingleShot(True)
                    self.pumpOn_timer.timeout.connect(lambda: self.arduino.send_command('B')) #Pump on
                    self.pumpOn_timer.start(12000)  # 12-second delay
                    self.timers.append(self.pumpOn_timer)

                    # Timer for retracting actuator 2 and 3 again
                    self.retract_time_2 = QTimer()
                    self.retract_time_2.setSingleShot(True)
                    self.retract_time_2.timeout.connect(lambda: self.arduino.send_command('K')) #Retract Act2 and Act3
                    self.retract_time_2.start(16000)  # 16-second delay
                    self.timers.append(self.retract_time_2)

                    self.calib_delay_timer = QTimer()
                    self.calib_delay_timer.setSingleShot(True)
                    self.calib_delay_timer.timeout.connect(lambda: self.arduino.send_command('D'))
                    self.calib_delay_timer.start(21000)  # 5-second delay
                    self.timers.append(self.calib_delay_timer)

                    self.opening_air_delay = QTimer()
                    self.opening_air_delay.setSingleShot(True)
                    self.opening_air_delay.timeout.connect(lambda: self.arduino.send_command('I'))
                    self.opening_air_delay.start(50000-10000)  # 4-second delay, wait for opening air.
                    self.timers.append(self.opening_air_delay)

                    self.after_closing_air_delay = QTimer()
                    self.after_closing_air_delay.setSingleShot(True)
                    self.after_closing_air_delay.timeout.connect(lambda: self.arduino.send_command('H'))                    
                    self.after_closing_air_delay.start(69000-10000)  # 4-second delay, wait for closing air sound then close air.
                    self.timers.append(self.after_closing_air_delay) 

                    self.opening_middle_valve_delay = QTimer()
                    self.opening_middle_valve_delay.setSingleShot(True)
                    self.opening_middle_valve_delay.timeout.connect(lambda: self.arduino.send_command('F'))
                    self.opening_middle_valve_delay.start(73000-10000)  # 2-second delay, wait for openning mid air to reduce pressure to 0.
                    self.timers.append(self.opening_middle_valve_delay)

                    self.post_opening_middle_valve_delay = QTimer()
                    self.post_opening_middle_valve_delay.setSingleShot(True)
                    self.post_opening_middle_valve_delay.timeout.connect(lambda: self.arduino.send_command('J'))
                    self.post_opening_middle_valve_delay.start(77000-10000)  # 4-second delay, wait for openning mid air to reduce pressure to 0 and then close air.
                    self.timers.append(self.post_opening_middle_valve_delay)

                    self.presnapshot_delay = QTimer()
                    self.presnapshot_delay.setSingleShot(True)
                    self.presnapshot_delay.timeout.connect(self.closeButton.click)
                    self.presnapshot_delay.start(78000-10000)
                    self.timers.append(self.presnapshot_delay)

                    self.pre2snapshot_delay = QTimer()
                    self.pre2snapshot_delay.setSingleShot(True)
                    self.pre2snapshot_delay.timeout.connect(self.viewButton.click)
                    self.pre2snapshot_delay.start(80000-10000)
                    self.timers.append(self.pre2snapshot_delay)

                    self.snapshot_delay = QTimer()
                    self.snapshot_delay.setSingleShot(True)
                    self.snapshot_delay.timeout.connect(self.Snap.click)
                    self.snapshot_delay.start(84000-10000) # 4-second delay, wait for openning mid air to reduce pressure to 0 and then close air.
                    self.timers.append(self.snapshot_delay)


                elif extracted_text == "UNLOCKED":
                    print('UNLOCKED')

                    self.stop_timer = QTimer()
                    self.stop_timer.setSingleShot(True)
                    self.stop_timer.timeout.connect(lambda: self.arduino.send_command('K'))
                    self.stop_timer.start(3000)  # 3-second delay before retracting actuator 2 and 3
                    self.timers.append(self.stop_timer)

                    self.calib_delay_timer = QTimer()
                    self.calib_delay_timer.setSingleShot(True)
                    self.calib_delay_timer.timeout.connect(lambda: self.arduino.send_command('D'))
                    self.calib_delay_timer.start(8000)  # 5-second delay
                    self.timers.append(self.calib_delay_timer)

                    self.opening_air_delay = QTimer()
                    self.opening_air_delay.setSingleShot(True)
                    self.opening_air_delay.timeout.connect(lambda: self.arduino.send_command('I'))
                    self.opening_air_delay.start(27000)  # 19-second delay, wait for opening air.
                    self.timers.append(self.opening_air_delay)

                    self.after_closing_air_delay = QTimer()
                    self.after_closing_air_delay.setSingleShot(True)
                    self.after_closing_air_delay.timeout.connect(lambda: self.arduino.send_command('H'))                    
                    self.after_closing_air_delay.start(46000)  # 4-second delay, wait for closing air sound then close air.
                    self.timers.append(self.after_closing_air_delay) 

                    self.opening_middle_valve_delay = QTimer()
                    self.opening_middle_valve_delay.setSingleShot(True)
                    self.opening_middle_valve_delay.timeout.connect(lambda: self.arduino.send_command('F'))
                    self.opening_middle_valve_delay.start(50000)  # 2-second delay, wait for openning mid air to reduce pressure to 0.
                    self.timers.append(self.opening_middle_valve_delay)

                    self.post_opening_middle_valve_delay = QTimer()
                    self.post_opening_middle_valve_delay.setSingleShot(True)
                    self.post_opening_middle_valve_delay.timeout.connect(lambda: self.arduino.send_command('J'))
                    self.post_opening_middle_valve_delay.start(54000)  # 4-second delay, wait for closing mid air to reduce pressure to 0 and then close air.
                    self.timers.append(self.post_opening_middle_valve_delay)

                    self.presnapshot_delay = QTimer()
                    self.presnapshot_delay.setSingleShot(True)
                    self.presnapshot_delay.timeout.connect(self.closeButton.click)
                    self.presnapshot_delay.start(55000)
                    self.timers.append(self.presnapshot_delay)

                    self.pre2snapshot_delay = QTimer()
                    self.pre2snapshot_delay.setSingleShot(True)
                    self.pre2snapshot_delay.timeout.connect(self.viewButton.click)
                    self.pre2snapshot_delay.start(57000)
                    self.timers.append(self.pre2snapshot_delay)

                    self.snapshot_delay = QTimer()
                    self.snapshot_delay.setSingleShot(True)
                    self.snapshot_delay.timeout.connect(self.Snap.click)
                    self.snapshot_delay.start(59000) # 4-second delay, wait for openning mid air to reduce pressure to 0 and then close air.
                    self.timers.append(self.snapshot_delay)
                else:
                    QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Could not process. Click GO again.")
                    self.confirmFinish() 
                    return 


    def startWebcam(self):
        if not self.is_webcam_open_first_time:            
            self.cap = cv2.VideoCapture(0)
            time.sleep(1)
            self.is_webcam_open_first_time = True
        else:
            self.cap = cv2.VideoCapture(0)
            
        if self.cap.isOpened():
            self.is_webcam_open = True
            self.timer = QTimer() # Set up timer for updating the frame
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)  # Update frame every 30 ms
        else: 
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Could not open webcam. Click View button again.")
            return

    def stop_webcam(self):
        self.timer.stop()
        self.cap.release()

    def exitWindow(self):
        MainWindow.close()


    def resetWindow(self):
        self.arduino.send_command('G') # Retract all linear actuators, close all valves, turn off pump controller.
        self.stop_webcam()
        
        QtWidgets.QApplication.closeAllWindows() # close the current active window
        
        self.new_window = QtWidgets.QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.new_window)
        self.new_window.showFullScreen()        

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
        font.setPointSize(30)  # Set a larger font size
        msgBox.setFont(font)
        msgBox.setWindowTitle('Confirm Start')
        msgBox.setStyleSheet(""" QMessageBox {
                                    min-width: 500px;  /* Set the minimum width */
                                    min-height: 300px;  /* Set the minimum height */
                                }
                                QPushButton {
                                    font-size: 30px;  /* Increase font size of buttons */
                                    padding: 20px;     /* Add padding to make buttons larger */
                                }
                                QLabel {
                                    font-size: 25px;  /* Increase font size of the label text */
                                }""")        
        msgBox.setText(
        "Are you sure you want to start?<br><br>"
        "<ul>"
        "<li>Have you connected the webcam?</li>"
        "<li>Have you connected the USB2 cable?</li>"
        "<li>Have you openned the air pressure?</li>"
        "</ul>"
        )
        
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.No)

        response = msgBox.exec_()

        if response == QtWidgets.QMessageBox.Yes:
        #     QtWidgets.QMessageBox.warning(self.centralwidget, "Testing", "Start processS")
            self.startButton.setText("STOP")
            self.startButton.setStyleSheet("background-color: rgb(204, 0, 0);")
            self.is_running = True            
            self.start()  
        else: 
            return


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

    def confirmFinish(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
        font = QtGui.QFont()
        font.setPointSize(20)  # Set a larger font size
        msgBox.setFont(font)
        msgBox.setStyleSheet(""" QMessageBox {
                                    min-width: 500px;  /* Set the minimum width */
                                    min-height: 300px;  /* Set the minimum height */
                                }
                                QPushButton {
                                    font-size: 18px;  /* Increase font size of buttons */
                                    padding: 12px;     /* Add padding to make buttons larger */
                                }
                                QLabel {
                                    font-size: 25px;  /* Increase font size of the label text */
                                }""")
        msgBox.setWindowTitle('Confirm Finished')
        msgBox.setText('Finished. Click YES')
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Yes)

        response = msgBox.exec_()

        if response == QtWidgets.QMessageBox.Yes:
            self.finish()

    def confirmStop(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
        font = QtGui.QFont()
        font.setPointSize(20)  # Set a larger font size
        msgBox.setFont(font)
        msgBox.setStyleSheet(""" QMessageBox {
                                    min-width: 600px;  /* Set the minimum width */
                                    min-height: 300px;  /* Set the minimum height */
                                }
                                QPushButton {
                                    font-size: 25px;  /* Increase font size of buttons */
                                    padding: 15px;     /* Add padding to make buttons larger */
                                }
                                QLabel {
                                    font-size: 30px;  /* Increase font size of the label text */
                                }""")
        msgBox.setWindowTitle('Confirm Stop')
        msgBox.setText('Are you sure you want to stop?')        
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.No)
        response = msgBox.exec_()
        if response == QtWidgets.QMessageBox.Yes:
            self.is_confirmStop_Yes = True
            self.stop()
        elif response == QtWidgets.QMessageBox.No:
            self.is_confirmStop_Yes = False
            
    
    def finish(self):
        self.startButton.setText("GO")
        self.startButton.setStyleSheet("background-color: rgb(138, 226, 52);")
        self.is_running = False

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
            image_filename = f"/home/billy/GUI/SnapShotImages/processed_snapshot_simple{timestamp}.jpg"         
            image_filename2 = f"/media/billy/3438-6131/Images/processed_snapshot_simple{timestamp}.jpg"
            # Save the processed image for OCR
            cv2.imwrite(image_filename2, cropped_frame)
                        


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    splash = LoadingSplashScreen("1488.gif") 
    splash.show()
    app.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
    MainWindow = QtWidgets.QMainWindow()
    QTimer.singleShot(8000, lambda: (splash.stop_animation(), MainWindow.showFullScreen()))
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    sys.exit(app.exec_())
