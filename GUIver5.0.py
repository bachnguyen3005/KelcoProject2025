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
        uic.loadUi('GUIver5.0.ui', self)
        
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
            self.startButton.setText("GO")
            self.startButton.setStyleSheet("background-color: rgb(138, 226, 52);")
            self.is_running = False
            return
    
    def snapshot(self):
        ret, frame = self.cap.read()
        if ret:
            #Rectangle shape
            rect_width = 400 
            rect_height = 100 
            rect_x = 120
            rect_y = 280
            # Crop the frame to the size of the red rectangle
            cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"/home/dinh/Documents/PlatformIO/Projects/kelco_test_001/SnapShotImages/processed_snapshot_simple{timestamp}.jpg"                 
            # Save the processed image for OCR
            cv2.imwrite(image_filename, cropped_frame)
            result_number= self.ocr_processor.extract_numbers(image_filename)
            if result_number == "ERROR":
                QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Error")
                # self.confirmFinish()
            else: # Successfully extract text 
                print(result_number)

                kPa = result_number[0]
                Cal = result_number[1]

                self.kpaNumber.setText(str(kPa))
                self.calNumber.setText(str(Cal))

                if kPa == 0:
                    self.lowVoltageTestResult.setText('OK')
                    # self.confirmFinish()
                else:
                    self.lowVoltageTestResult.setText('ERROR')
                    # self.confirmFinish()
    
    def initialize_ocr(self): 
        self.ocr_processor = OCRProcessor()
    
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
    
    def start(self):
        self.calNumber.setText('--')  # Reset the value to 0
        self.kpaNumber.setText('--')  # Reset the value to 0
        self.lowVoltageTestResult.setText('--') # Reset value
        self.highVoltageTestResult.setText('--') # Reset value
        if not self.is_webcam_open:
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "ERROR")
            return
        # Initialize state machine if it doesn't exist
        if not hasattr(self, 'state_machine'):
            self.state_machine = ArduinoStateMachine(self.arduino, self)
        # Reset the state machine to IDLE state
        self.state_machine.current_state = "IDLE"
        # Start the initial sequence
        self.arduino.send_command('CMD_PUMP_SEQUENCE')  # Extend actuators and pump ON
        
        # Set up state machine monitoring
        self.state_machine.sequence_timer = QTimer()
        self.state_machine.sequence_timer.timeout.connect(self.monitor_arduino_responses)
        self.state_machine.sequence_timer.start(100)  # Check every 100ms
        
        # Keep a reference to the timer for cleanup
        self.timers.append(self.state_machine.sequence_timer)   

    def monitor_arduino_responses(self):
        response = self.arduino.read_command() 
        if response:
            print(f"Received response: {response}")      
            if response == "L":
                self.state_machine.sequence_timer.stop() #Stop sequence timer
                ret, frame = self.cap.read()
                if ret:
                    rect_width = 400 
                    rect_height = 100 
                    rect_x = 120
                    rect_y = 280
                    cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_filename = f"KelcoProject2025/SnapShotImages/processed_snapshot_LOCK2UNLOCK{timestamp}.jpg"
                    cv2.imwrite(image_filename, cropped_frame) 
                    # Perform OCR
                    extracted_text = self.ocr_processor.get_lock_status(image_filename)
                    print(f"OCR Result: {extracted_text}")
                    # Start the appropriate sequence based on OCR result
                    if extracted_text == "LOCKED" or extracted_text == "UNLOCKED":
                        self.state_machine.start_sequence(extracted_text)
                    else:
                        QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", 
                                                    "Could not recognize lock status. Please try again.")
                        self.confirmFinish()

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

    def confirm_finish(self): 
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
                
class ArduinoStateMachine:
    def __init__(self, arduino_communicator, gui_instance):
        self.arduino = arduino_communicator
        self.gui = gui_instance
        self.current_state = "IDLE"
        self.sequence_timer = None
        self.ui_actions_needed = False
        
    def start_sequence(self, ocr_result):
        if ocr_result == "LOCKED":
            self.arduino.send_command('LOCKED_SEQUENCE')
            self.current_state = "EXECUTING_LOCKED_SEQUENCE"
            # Start monitoring for status updates
            self.start_monitoring()
        elif ocr_result == "UNLOCKED":
            self.arduino.send_command('UNLOCKED_SEQUENCE') 
            self.current_state = "EXECUTING_UNLOCKED_SEQUENCE"
            self.start_monitoring()
    
    def start_monitoring(self):
        # Set up a timer to check for Arduino status updates
        self.sequence_timer = QTimer()
        self.sequence_timer.timeout.connect(self.check_status)
        self.sequence_timer.start(100)  # Check every 100ms
    
    def check_status(self):
        response = self.arduino.read_command()
        if response:
            if response == "PRESSED_RESET":
                print("PRESSED_RESET")
            elif response == "ACCESS_CALIBRATION_MODE":
                print("ACCESS_CALIBRATION_MODE")
            elif response == "PRESSED_P":
                print("PRESSED_P")
            elif response == "OPEN_AIR":
                print("OPEN_AIR")
            elif response == "CLOSE_AIR":
                print("CLOSE_AIR")
            elif response == "MID_AIR_OPEN":
                print("MID_AIR_OPEN")
            elif response == "MID_AIR_CLOSE":
                print("MID_AIR_CLOSE")
            elif response == "SEQUENCE_COMPLETE":
                print("Arduino sequence completed")
                self.sequence_timer.stop()
                self.current_state = "WAITING_FOR_UI_ACTIONS"
                self.perform_ui_actions()
    
    def perform_ui_actions(self):
        self.gui.Snap.click() # Read kPa and Cal method

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())