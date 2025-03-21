from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QObject, QEvent
from PyQt5.QtGui import QImage, QPixmap, QPainter, QMovie
from ocr import OCRProcessor
from utils import SerialCommunicator
from led_detector import LEDDetector  
from webcam_thread import WebcamThread
from datetime import datetime
from port_selection import PortSelectionDialog
import serial
import sys
import time
import cv2
import traceback
import queue

from config import *

# Custom stream class to redirect stdout to our GUI
class OutputStreamRedirector(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.last_message = ""
        
    def write(self, text):
        # Store the original stdout for debugging
        sys.__stdout__.write(text)
        
        # Only update the widget if it's not empty (ignoring newlines)
        if text.strip():
            self.last_message = text.strip()
            # Use the Qt signal-slot mechanism to update the UI from any thread
            QtCore.QMetaObject.invokeMethod(
                self.text_widget, 
                "setText", 
                Qt.QueuedConnection,
                QtCore.Q_ARG(str, self.last_message)
            )
    
    def flush(self):
        pass

class MainWindow(QtWidgets.QMainWindow):
    # Define a high-priority emergency stop signal
    emergency_signal = pyqtSignal()
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Load the UI file directly
        uic.loadUi('GUIver5.2.ui', self)
        
        # Connect the emergency signal
        self.emergency_signal.connect(self.perform_emergency_stop, Qt.QueuedConnection)
        
        # Setup stdout redirection to logMessageLine
        self.stdout_redirector = OutputStreamRedirector(self.logMessageLine)
        sys.stdout = self.stdout_redirector
        
        self.webcam_index, self.arduino_port, self.arduino_baudrate = self.get_user_connection_preferences()
        
        # Now you can access UI elements directly
        self.populate_model_list()
        
        # Initialize webcam thread
        self.webcam_thread = WebcamThread()
        self.webcam_thread.update_frame_signal.connect(self.update_frame_from_thread)
        
        self.is_webcam_open = False
        self.is_webcam_open_first_time = False
        self.is_running = False  # Track the current state (GO/STOP)
        self.timers = []  # List to store all the timers
        
        try:
            # Directly use SerialCommunicator from utils
            self.arduino = SerialCommunicator(port=self.arduino_port, baudrate=self.arduino_baudrate, timeout=1)
            print("✅ Arduino connected successfully")
        except Exception as e:
            print(f"Error initializing Arduino: {str(e)}")
            self.arduino = None
        
        # Initialize the LED detector
        self.led_detector = LEDDetector()
        
        # Add box coordinates for LED detection
        self.led_box_coordinates = [
            [56, 269, 37, 37], 
            [60, 329, 36, 33],
            [65, 383, 40, 34]
        ]
        # Connect signals - use installEventFilter for the stop button
        self.startButton.installEventFilter(self)
        self.viewButton.clicked.connect(self.start_webcam)
        self.closeButton.clicked.connect(self.stop_webcam)
        self.Snap.clicked.connect(self.snapshot)
        
        # Initialize GUI state
        self.startButton.setText("GO")
        
        # Arduino monitoring timer
        self.arduino_timer = QTimer()
        self.arduino_timer.timeout.connect(self.check_arduino_responses)
        
        # Initialize components
        QTimer.singleShot(0, self.initialize_ocr)
        QTimer.singleShot(0, self.start_webcam)
    
    def eventFilter(self, obj, event):
        """Custom event filter for high-priority button events"""
        if obj == self.startButton and event.type() == QEvent.MouseButtonPress:
            if self.is_running:
                # Emit the emergency signal immediately
                self.emergency_signal.emit()
                return True  # Event handled
            else:
                # Let normal click handling proceed
                QTimer.singleShot(0, self.toggle_Go_Stop)
                return True  # Event handled
                
        # Pass other events to the base class
        return super().eventFilter(obj, event)
    
    def __del__(self):
        # Restore original stdout when the application is closed
        sys.stdout = sys.__stdout__
    
    def populate_model_list(self):
        # Add items to the combo box
        models = ["F60", "E30", "IPG20", "F29"]
        self.modelList.addItems(models)
    
    def start_webcam(self):
        # Stop any existing webcam thread first
        if hasattr(self, 'webcam_thread') and self.webcam_thread.running:
            self.webcam_thread.stop_capture()
        
        # Determine camera index
        camera_index = self.webcam_index
                
        # Start the webcam thread
        if self.webcam_thread.start_capture(camera_index):
            self.is_webcam_open = True
            print("✅ Webcam started ✅")
        else:
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", 
                                        "Could not open webcam")

    def stop_webcam(self):
        if self.is_webcam_open:
            for timer in self.timers:
                if timer.isActive():
                    timer.stop()
            self.timers.clear()
            
            if hasattr(self, 'cap'):
                self.cap.release()
            
            self.is_webcam_open = False
            self.webcamFrame.clear()
            print("Webcam stopped")
    
    def update_frame_from_thread(self, qt_image):
        # Convert QImage to QPixmap and display
        qt_pixmap = QPixmap.fromImage(qt_image)
        self.webcamFrame.setPixmap(qt_pixmap)
        self.webcamFrame.setAlignment(Qt.AlignCenter)
        self.draw_red_rectangle()
     
    def toggle_Go_Stop(self):
        print(f"Toggle button pressed, current state: {'Running' if self.is_running else 'Stopped'}")
        if not self.is_running:
            # Start the process
            self.confirm_start()
        else:
            # Stop everything immediately using the emergency stop
            self.perform_emergency_stop()
    
    def perform_emergency_stop(self):
        print("🚨 EMERGENCY STOP ACTIVATED 🚨")
        
        # First, set flags to indicate we're stopping
        self.is_running = False
        
        # Stop Arduino monitoring timer
        if self.arduino_timer.isActive():
            self.arduino_timer.stop()
        
        # Stop all timers
        for timer in self.timers:
            if timer.isActive():
                timer.stop()
        self.timers.clear()
        
        # Send STOP command to Arduino
        if self.arduino:
            try:
                self.arduino.send_command('STOP')
                print("STOP command sent to Arduino")
                
                # Clear any data in the serial buffer
                time.sleep(0.1)  # Short delay to allow Arduino to process
                while self.arduino.read_command():
                    pass  # Empty the buffer
            except Exception as e:
                print(f"Error sending emergency stop: {e}")
        
        # Reset UI elements
        self.startButton.setText("GO")
        
        # Cancel any ongoing message boxes
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if isinstance(widget, QtWidgets.QMessageBox):
                widget.close()
        
        # Process events to ensure UI updates
        QApplication = QtWidgets.QApplication.instance()
        QApplication.processEvents()
        
        print("System emergency stopped")
    
    def snapshot(self):
        if not self.is_running:
            print("System not running, snapshot cancelled")
            return
                
        try:
            # Get the latest frame directly from the thread
            frame = self.webcam_thread.get_latest_frame()
            
            if frame is not None:
                # Crop the frame to the size of the red rectangle
                cropped_frame = frame[OCR_RECT_Y:OCR_RECT_Y + OCR_RECT_HEIGHT, OCR_RECT_X:OCR_RECT_X + OCR_RECT_WIDTH]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"/home/dinh/Documents/PlatformIO/Projects/kelco_test_001/SnapShotImages/processed_snapshot_simple{timestamp}.jpg"                 
                
                # Save the processed image for OCR
                cv2.imwrite(image_filename, cropped_frame)
                
                # Process OCR directly
                result_number = self.ocr_processor.extract_numbers(image_filename)
                
                # Check if we're still running after OCR
                if not self.is_running:
                    return
                    
                # Handle OCR result
                if result_number == "ERROR":
                    # Only show message box if still running
                    if self.is_running:
                        QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Error extracting data")
                        self.finish()
                else: # Successfully extract text 
                    print(f"OCR Result: {result_number}")

                    kPa = result_number[0]
                    Cal = result_number[1]

                    self.kpaNumber.setText(str(kPa))
                    self.calNumber.setText(str(Cal))

                    if kPa == 0:
                        self.lowVoltageTestResult.setText('PASS')
                        self.arduino.send_command('PRESS_P')
                        # self.finish() #Comment out to continue to test the paddle flow 
                        if(self.modelList.currentText() == "F60"):
                            return
                        else:
                            self.finish()
                        
                    else:
                        self.lowVoltageTestResult.setText('ERROR')
                        if(self.modelList.currentText() == "F60"):
                            return
                        else:
                            self.finish()
            else:
                print("Error: No frame available from webcam")
                        
        except Exception as e:
            print(f"Error in snapshot: {str(e)}")
            traceback.print_exc()
    
    def initialize_ocr(self): 
        try:
            self.ocr_processor = OCRProcessor()
            print("✅ OCR system initialized")
        except Exception as e:
            print(f"Error initializing OCR: {str(e)}")
            traceback.print_exc()
    
    def confirm_start(self):
        # Create a custom dialog
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('Confirm Start')
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        
        # Set a clean, modern style for the dialog
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QCheckBox {
                spacing: 15px;
                padding: 10px;
            }
            QCheckBox::indicator {
                width: 30px;
                height: 30px;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 15px 30px;
                font-size: 20px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton#cancel {
                background-color: #e74c3c;
            }
            QPushButton#cancel:hover {
                background-color: #c0392b;
            }
        """)
        
        # Create layout for the dialog
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Add a label for the title
        title_label = QtWidgets.QLabel("Checklist before starting:")
        title_font = QtGui.QFont()
        title_font.setPointSize(25)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Create a widget for the checklist area with a light background
        checklist_widget = QtWidgets.QWidget()
        checklist_widget.setStyleSheet("background-color: white; border-radius: 10px;")
        checklist_layout = QtWidgets.QVBoxLayout(checklist_widget)
        checklist_layout.setContentsMargins(20, 20, 20, 20)
        checklist_layout.setSpacing(15)
        
        # Create checkboxes for each item
        checkbox_font = QtGui.QFont()
        checkbox_font.setPointSize(16)
        
        checkboxes = [
            QtWidgets.QCheckBox("Webcam is connected with your laptop"),
            QtWidgets.QCheckBox("USB cable is connected to your laptop"),
            QtWidgets.QCheckBox("You have openned air pressure")
        ]
        
        # Create icons for each checkbox (you can replace with actual icons if available)
        icons = [
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon),
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DriveFDIcon),
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton)
        ]
        
        # Add checkboxes to layout with icons
        for i, checkbox in enumerate(checkboxes):
            checkbox.setFont(checkbox_font)
            checkbox.setIcon(icons[i])
            checkbox.setIconSize(QtCore.QSize(30, 30))
            checklist_layout.addWidget(checkbox)
        
        # Add the checklist widget to the main layout
        layout.addWidget(checklist_widget)
        
        # Add stretch to push buttons to the bottom
        layout.addStretch()
        
        # Create button layout
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(20)
        
        # Create Start and Cancel buttons
        start_button = QtWidgets.QPushButton("START")
        cancel_button = QtWidgets.QPushButton("CANCEL")
        cancel_button.setObjectName("cancel")  # Set object name for specific styling
        
        # Add buttons to the button layout
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(start_button)
        
        # Add button layout to main layout
        layout.addLayout(button_layout)
        
        # Connect button signals
        start_button.clicked.connect(lambda: self.handle_start(dialog, checkboxes))
        cancel_button.clicked.connect(dialog.reject)
        
        # Show the dialog
        dialog.exec_()

    def handle_start(self, dialog, checkboxes):
        # Check if all boxes are checked
        all_checked = all(checkbox.isChecked() for checkbox in checkboxes)
        
        if not all_checked:
            # Find which items are not checked
            unchecked_items = [f"• {checkbox.text()}" for checkbox in checkboxes if not checkbox.isChecked()]
            unchecked_text = "\n".join(unchecked_items)
            
            # Create warning dialog if not all items are checked
            warning = QtWidgets.QMessageBox(dialog)
            warning.setIcon(QtWidgets.QMessageBox.Warning)
            warning.setWindowTitle("Incomplete Checklist")
            warning.setText("Please complete all checks before starting.")
            warning.setInformativeText("The following items are not checked:")
            warning.setDetailedText(unchecked_text)
            warning.setStandardButtons(QtWidgets.QMessageBox.Ok)
            
            # Style the warning
            warning.setStyleSheet("""
                QMessageBox {
                    background-color: #fff7e6;
                    font-size: 16px;
                }
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    padding: 10px 20px;
                    font-size: 16px;
                    border-radius: 5px;
                }
            """)
            
            warning.exec_()
        else:
            # All items checked, close the dialog and start
            dialog.accept()
            self.startButton.setText("STOP")
            self.is_running = True
            self.start()
    
    def start(self):
        # Reset UI elements
        self.calNumber.setText('--')
        self.kpaNumber.setText('--')
        self.paddleFlowTestResult.setText('--')
        self.lowVoltageTestResult.setText('--') 
        self.highVoltageTestResult.setText('--')
        
        if not self.is_webcam_open:
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "ERROR: Webcam not open")
            return
            
        if not self.arduino:
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Arduino not connected")
            return
        
        print("Starting sequence")
        
        # Send the PUMP_SEQ command directly
        try:
            self.arduino.send_command('PUMP_SEQ')
            
            # Start the Arduino monitoring timer
            self.arduino_timer.start(100)  # Check every 100ms
            self.timers.append(self.arduino_timer)
            
        except Exception as e:
            print(f"Error sending PUMP_SEQ command: {str(e)}")
            self.perform_emergency_stop()
            return

    def check_arduino_responses(self):
        """Check for responses from the Arduino"""
        if not self.is_running or not self.arduino:
            return
            
        try:
            response = self.arduino.read_command()
            if response:
                print(f"Received response: {response}")
                
                # Handle different responses
                if response == "DONE":
                    self.capture_lock_status()
                elif response == "PRESSED_RESET":
                    print("PRESSED_RESET")
                    self.logMessageLine.setText("PRESSED_RESET")
                elif response == "ACCESS_CALIBRATION_MODE":
                    print("ACCESS_CALIBRATION_MODE")
                    self.logMessageLine.setText("ACCESS_CALIBRATION_MODE")
                elif response == "PRESSED_P":
                    print("PRESSED_P")
                    self.logMessageLine.setText("PRESSED_P")
                elif response == "OPEN_AIR":
                    print("OPEN_AIR")
                    self.logMessageLine.setText("OPEN_AIR")
                elif response == "CLOSE_AIR":
                    print("CLOSE_AIR")
                    self.logMessageLine.setText("CLOSE_AIR")
                elif response == "MID_AIR_OPEN":
                    print("MID_AIR_OPEN")
                    self.logMessageLine.setText("MID_AIR_OPEN")
                elif response == "MID_AIR_CLOSE":
                    print("MID_AIR_CLOSE")
                    self.logMessageLine.setText("MID_AIR_CLOSE")
                elif response == "SEQUENCE_COMPLETE":
                    print("SEQUENCE_COMPLETE")
                    self.logMessageLine.setText("SEQUENCE_COMPLETE")
                    QTimer.singleShot(500, self.snapshot)  # Small delay to let everything settle
                elif response == "P_PRESSED_TWICE":
                    print(f"Current model: {self.modelList.currentText()}")
                    print("P_PRESSED_TWICE")
                    self.logMessageLine.setText("P_PRESSED_TWICE")   
                    self.arduino.send_command('PUSH_PADDLE')    
                    self.logMessageLine.setText("Start pushing paddle!")             
                elif response == "PADDLE_PUSHED":
                    print("PADDLE_PUSHED")
                    self.logMessageLine.setText("PADDLE_PUSHED")
                    QTimer.singleShot(1000, self.capture_led_state_F60)
                elif response == "BLINKING_TEST_F60":
                    print("BLINKING_TEST_F60")
                    self.logMessageLine.setText("BLINKING_TEST_F60")
                    self.check_blinking_led_F60()
                
                
        except Exception as e:
            print(f"Error reading from Arduino: {str(e)}")
    
    def capture_lock_status(self):
        """Capture and process the lock status"""
        if not self.is_running:
            return
                
        try:
            print("✅ Capturing lock status now...")
            
            # Give extra time for the display to stabilize
            for i in range(3):
                # Process events to ensure UI updates are rendered
                QApplication = QtWidgets.QApplication.instance()
                QApplication.processEvents()
                time.sleep(0.1)  # Short pauses
                
            # Get the latest frame directly from the thread
            frame = self.webcam_thread.get_latest_frame()
            
            if frame is not None:
                cropped_frame = frame[OCR_RECT_Y:OCR_RECT_Y + OCR_RECT_HEIGHT, OCR_RECT_X:OCR_RECT_X + OCR_RECT_WIDTH]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"/home/dinh/Documents/PlatformIO/Projects/kelco_test_001/SnapShotImages/LOCK2UNLOCK{timestamp}.jpg"
                cv2.imwrite(image_filename, cropped_frame)
                
                print("✅ Image captured and saved")
                
                # Process lock status directly
                extracted_text = self.ocr_processor.get_lock_status(image_filename)
                print(f"Lock status: {extracted_text}")
                
                # Start the appropriate sequence
                if extracted_text == "LOCKED" or extracted_text == "UNLOCKED":
                    command = 'LOCKED_SEQUENCE' if extracted_text == "LOCKED" else 'UNLOCKED_SEQUENCE'
                    print(f"Starting {extracted_text} sequence")
                    self.progressBar.setValue(50)
                    # Send command directly
                    self.arduino.send_command(command)
                    
                else:
                    # If we can't recognize the status, try again with a delay
                    print("Lock status not recognized, waiting to try again...")
                    QTimer.singleShot(2000, self.retry_capture_lock_status)
                    
            else:
                print("Error: Failed to capture frame from webcam")
                self.confirm_finish()
                        
        except Exception as e:
            print(f"Error capturing lock status: {str(e)}")
            traceback.print_exc()
            self.confirm_finish()
    
    def retry_capture_lock_status(self):
        """Retry capturing lock status after a delay"""
        if self.is_running:
            self.capture_lock_status()
        
    def finish(self):
        # Only reset if we're still running
        if self.is_running:
            self.startButton.setText("GO")
            self.is_running = False
            
            # Stop Arduino monitoring
            if self.arduino_timer.isActive():
                self.arduino_timer.stop()
                
            print("Process finished")
        
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
        # Draw the hollow rectangle
        painter.drawRect(OCR_RECT_X, OCR_RECT_Y, OCR_RECT_WIDTH, OCR_RECT_HEIGHT)      
        # End painting
        painter.end()
        # Update the label with the modified pixmap
        self.webcamFrame.setPixmap(pixmap)

    def confirm_finish(self): 
        # Check if we're still running before showing dialog
        if not self.is_running:
            return
            
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        font = QtGui.QFont()
        font.setPointSize(20)  # Set a larger font size
        msgBox.setWindowTitle('Confirm Finished')
        msgBox.setText('Finished')
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Yes)
        response = msgBox.exec_()
        if response == QtWidgets.QMessageBox.Yes:
            self.finish()

    def error(self):
        # Check if we're still running before showing dialog
        if not self.is_running:
            return
            
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Critical)
        font = QtGui.QFont()
        font.setPointSize(20)  # Set a larger font size
        msgBox.setWindowTitle('Error')
        msgBox.setText('Error occured! Please try again')
        self.finish()

    def capture_led_state_F60(self):
        """Capture the current state of the LEDs for verification"""
        if not self.is_running:
            return
            
        try:
            print("Capturing LED states...")
            
            # Get the latest frame from the webcam
            frame = self.webcam_thread.get_latest_frame()
            
            if frame is not None:
                # Save a copy of the frame for reference
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"/home/dinh/Documents/PlatformIO/Projects/kelco_test_001/SnapShotImages/led_verification_{timestamp}.jpg"
                cv2.imwrite(image_filename, frame)
                
                # Process the frame to detect LEDs
                results, display_img = self.led_detector.detect_leds(frame, self.led_box_coordinates)
                
                # Save the annotated image
                cv2.imwrite(f"/home/dinh/Documents/PlatformIO/Projects/kelco_test_001/SnapShotImages/led_detection_{timestamp}.jpg", 
                           cv2.cvtColor(display_img, cv2.COLOR_RGB2BGR))
                
                # Verify if exactly 2 green LEDs are lit
                verification_success, message = self.led_detector.check_green_leds(results)
                
                # Log detailed results
                print("\nLED Detection Results:")
                for result in results:
                    print(f"Box {result['box_id']} ({result['position']}): LED is {'ON' if result['lit'] else 'OFF'}")
                    if result['lit']:
                        print(f"  Color: {result['color']}")
                        print(f"  Brightness: {result['brightness']:.2f}")
                
                print(message)
                
                # Update the GUI with the result
                if verification_success:
                    #Continue with blinking test
                    self.arduino.send_command("START_BLINKING_TEST_F60")
                    self.logMessageLine.setText("Push back the paddle to intial position!")
                    # self.paddleFlowTestResult.setText('PASS')
                    
                else:
                    self.paddleFlowTestResult.setText('FAIL')
                
                # Now we can finish the test
                # self.finish()
            else:
                print("Error: Could not capture frame for LED verification")
                self.paddleFlowTestResult.setText('ERROR')
                self.finish()
                
        except Exception as e:
            print(f"Error in LED verification: {str(e)}")
            traceback.print_exc()
            self.highVoltageTestResult.setText('ERROR')
            self.finish()
        
    def get_user_connection_preferences(self):
        """Show dialog to get user's webcam and Arduino preferences"""
        dialog = PortSelectionDialog(self)
        
        # Set initial default values
        webcam_index = 2  # Default webcam index
        arduino_port = SERIAL_PORT  # Default from config
        arduino_baudrate = SERIAL_BAUDRATE  # Default from config
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            # User clicked OK, get their selections
            webcam_index, arduino_port, arduino_baudrate = dialog.get_selected_values()
            
            # Show a confirmation message with the selected options
            QtWidgets.QMessageBox.information(
                self,
                "Connection Settings",
                f"Selected webcam: {webcam_index if webcam_index >= 0 else 'None'}\n"
                f"Selected Arduino port: {arduino_port if arduino_port else 'None'}\n"
                f"Selected baudrate: {arduino_baudrate}"
            )
        else:
            # User clicked Cancel, show a message that we'll use defaults
            QtWidgets.QMessageBox.information(
                self,
                "Using Defaults",
                "Using default connections:\n"
                f"Webcam: {webcam_index}\n"
                f"Arduino port: {arduino_port}\n"
                f"Baudrate: {arduino_baudrate}"
            )
            
        return webcam_index, arduino_port, arduino_baudrate    
    
    def check_blinking_led_F60(self):
        """
        Check if the LED at position 2 (index 1) is blinking correctly
        This method is designed to be called from the MainWindow class
        """
        if not self.is_running:
            return
        
        try:
            print("Checking if LED at position 2 is blinking...")
            
            # First, take multiple frames to detect blinking
            blink_results = self.led_detector.detect_blinking_led(
                self.webcam_thread,
                self.led_box_coordinates,
                position_index=1,  # Position 2 (0-based index)
                num_frames=30,     # Take 15 frames
                interval_ms=200    # 100ms between frames
            )
            
            # Update GUI based on results
            if blink_results['is_blinking']:
                print("✅ LED at position 2 is blinking correctly")
                self.paddleFlowTestResult.setText('PASS')
            else:
                if blink_results['frames_on'] > 0:
                    print("⚠️ LED at position 2 is on but not blinking")
                    self.paddleFlowTestResult.setText('PASS')
                    
                else:
                    print("❌ LED at position 2 is not lighting up")
                    self.paddleFlowTestResult.setText('FAIL')
            
            # After LED verification is complete, we can continue with remaining
            # test steps or finish the test
            self.finish()
                
        except Exception as e:
            print(f"Error in blinking LED verification: {str(e)}")
            traceback.print_exc()
            self.highVoltageTestResult.setText('ERROR')
            self.finish()    
            
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")  # Use the cross-platform Fusion style
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())