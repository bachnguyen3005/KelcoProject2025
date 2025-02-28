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
            image_filename = f"KelcoProject2025/SnapShotImages/processed_snapshot_simple{timestamp}.jpg"                 
            # Save the processed image for OCR
            cv2.imwrite(image_filename, cropped_frame)
            result_number= self.ocr_processor.extract_numbers(image_filename)
            if result_number == "ERROR":
                QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Error")
                self.confirmFinish()
            else: # Successfully extract text 
                print(result_number)

                kPa = result_number[0]
                Cal = result_number[1]

                self.kpaNumber.setText(str(kPa))
                self.calNumber.setText(str(Cal))

                # if kPa == 0:
                #     print('Green')
                #     self.arduino.send_command('E')  # Turn on Green LED then press P twice
                #     self.confirmFinish()
                # else:
                #     QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Need to be calibrated manually")
                #     self.confirmFinish()
                    # delta = 50 - Cal  # Calculate the difference from the target calibration

                    # self.max_try = 0  # Initialize try counter
                    
                    # if delta < 5:
                    #     while kPa != 0 and self.max_try < 5:
                    #         print("Pressing UP ARROW")
                    #         self.arduino.send_command('Q')  # Send command to press the UP ARROW

                    #         # Wait for Arduino's response
                    #         while True:
                    #             response = self.arduino.read_command()
                    #             if response == "Q":
                    #                 break

                    #         # Capture a new image for OCR processing
                    #         ret, frame = self.cap.read()
                    #         if ret:
                    #             rect_width = 470  # Latest version of the dimensions
                    #             rect_height = 120
                    #             rect_x = 100
                    #             rect_y = 160

                    #             # Crop the frame to the red rectangle's size
                    #             cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]
                    #             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    #             image_filename = f"/home/billy/GUI/SnapShotImages/processed_snapshot_FAULT{timestamp}.jpg"

                    #             # Save the processed image for OCR
                    #             cv2.imwrite(image_filename, cropped_frame)

                    #             # Perform OCR on the cropped image
                    #             result_number_calib = self.ocr_processor.extract_numbers(image_filename)

                    #             if result_number_calib == "ERROR":
                    #                 print("ERROR")
                    #                 QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Webcam cannot focus. Please check again!")
                    #                 self.confirmFinish()                                    
                    #             else:
                    #                 # Extract and display the new kPa and Cal values
                    #                 current_kPa = result_number_calib[0]
                    #                 current_Cal = result_number_calib[1]

                    #                 self.kpaLCDNumber.display(current_kPa)
                    #                 self.calLCDNumber.display(current_Cal)

                    #                 # Update delta and retry counter
                    #                 delta = 50 - current_Cal
                    #                 self.max_try += 1
                                    
                    #                 if current_kPa == 0:
                    #                     print("Calibrate successfully")
                    #                     self.confirmFinish()
                    #                     break

                    #     if self.max_try >= 5:
                    #         print("Max attempts reached. Calibration failed.")
                    #         QtWidgets.QMessageBox.warning(self.centralwidget, "Max attempts reached. Calibration failed.")                            
                    #         self.confirmFinish()

                            
                                 
                    # elif -5 < delta < 0: #Cal > 50 and Cal < 55
                    #     while kPa != 0 and self.max_try < 5:
                    #         print("Pressing DOWN ARROW")
                    #         self.arduino.send_command('S')  # Send command to press the UP ARROW

                    #         # Wait for Arduino's response
                    #         while True:
                    #             response = self.arduino.read_command()
                    #             if response == "S":
                    #                 break

                    #         # Capture a new image for OCR processing
                    #         ret, frame = self.cap.read()
                    #         if ret:
                    #             rect_width = 470  # Latest version of the dimensions
                    #             rect_height = 120
                    #             rect_x = 100
                    #             rect_y = 160

                    #             # Crop the frame to the red rectangle's size
                    #             cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]
                    #             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    #             image_filename = f"/home/billy/GUI/SnapShotImages/processed_snapshot_FAULT{timestamp}.jpg"

                    #             # Save the processed image for OCR
                    #             cv2.imwrite(image_filename, cropped_frame)

                    #             # Perform OCR on the cropped image
                    #             result_number_calib = self.ocr_processor.extract_numbers(image_filename)

                    #             if result_number_calib == "ERROR":
                    #                 print("ERROR")
                    #                 QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Webcam cannot focus. Please check again!")
                    #                 self.confirmFinish()                                    
                    #             else:
                    #                 # Extract and display the new kPa and Cal values
                    #                 current_kPa = result_number_calib[0]
                    #                 current_Cal = result_number_calib[1]

                    #                 self.kpaLCDNumber.display(current_kPa)
                    #                 self.calLCDNumber.display(current_Cal)

                    #                 # Update delta and retry counter
                    #                 delta = 50 - current_Cal
                    #                 self.max_try += 1
                                    
                    #                 if current_kPa == 0:
                    #                     print("Calibrate successfully")
                    #                     self.confirmFinish()
                    #                     break

                    #     if self.max_try >= 5:
                    #         print("Max attempts reached. Calibration failed.")
                    #         QtWidgets.QMessageBox.warning(self.centralwidget, "Max attempts reached", "Calibration failed.")                            
                    #         self.confirmFinish()
                
                                    
                    # else:
                    #     QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Unable to calibrate. Check this again!")
                    #     self.confirmFinish() 
    
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
        self.calNumber.setText('0') # Reset the value to 0
        self.kpaNumber.setText('0') # Reset the value to 0
        if self.is_webcam_open:
            self.arduino.send_command('CMD_PUMP_SEQUENCE')  # Extend the actuator 2 and 3 and pump ON

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
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "ERROR")
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

    def after_delay(self, response, command2check):
        if response == command2check:
            ret, frame = self.cap.read()
            if ret:
                # Process and crop the frame for OCR
                rect_width = 400 
                rect_height = 100 
                rect_x = 120
                rect_y = 280
                cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width] # Crop LCD image 
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") # Save the cropped image 
                image_filename = f"KelcoProject2025/SnapShotImages/processed_snapshot_LOCK2UNLOCK{timestamp}.jpg"

                # Save the processed image for OCR
                cv2.imwrite(image_filename, cropped_frame)

                # Perform OCR on the cropped image
                extracted_text = self.ocr_processor.get_lock_status(image_filename)
                print(extracted_text)

                # Perform further actions based on OCR result
                if extracted_text == "LOCKED":
                    
                    self.stop_timer = QTimer()
                    self.stop_timer.setSingleShot(True)
                    self.stop_timer.timeout.connect(lambda: self.arduino.send_command('CMD_RETRACT_BOTH'))
                    self.stop_timer.start(3000)  # 3-second delay before retracting actuator 2 and 3
                    self.timers.append(self.stop_timer)

                    # Timer for second action: retract_button_2.click() (Turn off the pump controller)
                    self.retract_timer = QTimer()
                    self.retract_timer.setSingleShot(True)
                    self.retract_timer.timeout.connect(lambda: self.arduino.send_command('CMD_PUMP_OFF')) #Pump off
                    self.retract_timer.start(6000)  # 6-second delay
                    self.timers.append(self.retract_timer)

                    # Timer for third action: send_command('R') to extend actuators 2 and 3
                    self.command_timer = QTimer()
                    self.command_timer.setSingleShot(True)
                    self.command_timer.timeout.connect(lambda: self.arduino.send_command('CMD_EXTEND_BOTH')) #Extend Act2 and Act3
                    self.command_timer.start(9000)  # 9-second delay
                    self.timers.append(self.command_timer)

                    # Timer for fourth action: Turn off the controller
                    self.pumpOn_timer = QTimer()
                    self.pumpOn_timer.setSingleShot(True)
                    self.pumpOn_timer.timeout.connect(lambda: self.arduino.send_command('CMD_PUMP_ON')) #Pump on
                    self.pumpOn_timer.start(12000)  # 12-second delay
                    self.timers.append(self.pumpOn_timer)

                    # Timer for retracting actuator 2 and 3 again
                    self.retract_time_2 = QTimer()
                    self.retract_time_2.setSingleShot(True)
                    self.retract_time_2.timeout.connect(lambda: self.arduino.send_command('CMD_RETRACT_BOTH')) #Retract Act2 and Act3
                    self.retract_time_2.start(16000)  # 16-second delay
                    self.timers.append(self.retract_time_2)

                    self.calib_delay_timer = QTimer()
                    self.calib_delay_timer.setSingleShot(True)
                    self.calib_delay_timer.timeout.connect(lambda: self.arduino.send_command('CMD_FULL_SEQUENCE'))
                    self.calib_delay_timer.start(21000)  # 5-second delay
                    self.timers.append(self.calib_delay_timer)

                    self.opening_air_delay = QTimer()
                    self.opening_air_delay.setSingleShot(True)
                    self.opening_air_delay.timeout.connect(lambda: self.arduino.send_command('CMD_AIR_OPEN'))
                    self.opening_air_delay.start(50000-10000)  # 4-second delay, wait for opening air.
                    self.timers.append(self.opening_air_delay)

                    self.after_closing_air_delay = QTimer()
                    self.after_closing_air_delay.setSingleShot(True)
                    self.after_closing_air_delay.timeout.connect(lambda: self.arduino.send_command('CMD_AIR_CLOSE'))                    
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
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())