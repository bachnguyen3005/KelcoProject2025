from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QImage, QPixmap, QPainter, QMovie
from ocr import OCRProcessor
from utils import SerialCommunicator
import serial
import sys
from datetime import datetime
import time
import cv2

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Load the UI file directly
        uic.loadUi('GUIver4.1.ui', self)
        
        # Now you can access UI elements directly
        self.populate_model_list()
        
        self.is_webcam_open = False
        self.is_webcam_open_first_time = False
        self.is_running = False  # Track the current state (GO/STOP)
        self.timers = []  # List to store all the timers
        # self.arduino = SerialCommunicator(port='/dev/ttyUSB0', baudrate=115200, timeout=1)
        # Connect signals
        self.startButton.clicked.connect(self.on_start_clicked)
        self.viewButton.clicked.connect(self.start_webcam)
        self.closeButton.clicked.connect(self.stop_webcam)
        self.startButton.clicked.connect(self.toggle_Go_Stop)
        self.Snap.clicked.connect(self.snapshot)
        QTimer.singleShot(0, self.initialize_ocr)
        QTimer.singleShot(0, self.start_webcam)
        
    def populate_model_list(self):
        # Add items to the combo box
        models = ["F60", "E30", "IPG20", "F29"]
        self.modelList.addItems(models)
        
    def on_start_clicked(self):
        # Handle the start button click
        selected_model = self.modelList.currentText()
        self.lowVoltageTestResult.setText("OK")
        self.highVoltageTestResult.setText("ERROR")
        self.kpaNumber.setText("495")
        print(f"Test started for model: {selected_model}")

    def start_webcam(self):
        if not self.is_webcam_open_first_time:            
            self.cap = cv2.VideoCapture(2)
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
        pass 
    
    def toggle_Go_Stop(self):
        if not self.is_running:
            # Start the process
            self.confirm_start()
        else:
            # Stop the process
            self.confirm_stop()
            if self.is_confirmStop_Yes:
                self.startButton.setText("GO")
                self.startButton.setStyleSheet("background-color: rgb(138, 226, 52);")
                self.is_running = False
            elif self.is_confirmStop_Yes == False:
                return
    
    def snapshot(self):
        pass
    
    def initialize_ocr(self): 
        pass
    
    def confirm_start(self):
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
        "Check list before starting<br><br>"
        "<ul>"
        "<li>Make sure the webcam is connected with your laptop</li>"
        "<li>Make sure that USB2 is connected to your laptop</li>"
        "<li>Make sure that you have open air pressure</li>"
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
    
    def confirm_stop(self):
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

    def start(self):
        self.calNumber.setText('0') # Reset the value to 0
        self.kpaNumber.setText('0') # Reset the value to 0
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

    def finish(self):
        self.startButton.setText("GO")
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
        rect_width = 400 
        rect_height = 100 
        rect_x = 120
        rect_y = 280
        
        # Draw the hollow rectangle
        painter.drawRect(rect_x, rect_y, rect_width, rect_height)
        
        # End painting
        painter.end()
        
        # Update the label with the modified pixmap
        self.webcamFrame.setPixmap(pixmap)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())