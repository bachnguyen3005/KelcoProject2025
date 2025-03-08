from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QObject, QEvent
from PyQt5.QtGui import QImage, QPixmap, QPainter, QMovie
from ocr import OCRProcessor
from utils import SerialCommunicator
import serial
import sys
from datetime import datetime
import time
import cv2
import traceback
import queue
from webcam_thread import WebcamThread

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

# Custom Serial Communicator wrapper with command queue
class SafeSerialCommunicator:
    def __init__(self, serial_comm):
        self.serial_comm = serial_comm
        self.command_queue = queue.Queue()
        self.interrupt_requested = False
        self.is_processing = False
        self.command_timer = QTimer()
        self.command_timer.timeout.connect(self.process_command_queue)
        self.command_timer.start(50)  # Process queue every 50ms
    
    def send_command(self, command):
        """Queue a command to be sent to Arduino"""
        if self.interrupt_requested:
            print(f"Command '{command}' ignored due to interrupt")
            return False
            
        self.command_queue.put(command)
        return True
    
    def read_command(self):
        """Read response from Arduino"""
        if self.interrupt_requested:
            return None
            
        try:
            return self.serial_comm.read_command()
        except Exception as e:
            print(f"Error reading command: {e}")
            return None
    
    def interrupt(self):
        """Interrupt all operations and clear command queue"""
        self.interrupt_requested = True
        
        # Clear the command queue
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
            except queue.Empty:
                break
        
        # Send emergency stop command directly
        try:
            self.serial_comm.send_command('STOP')
            print("EMERGENCY STOP command sent directly to Arduino")
            
            # Clear any data in the serial buffer
            time.sleep(0.1)  # Short delay to allow Arduino to process
            while self.serial_comm.read_command():
                pass  # Empty the buffer
                
        except Exception as e:
            print(f"Error sending emergency stop: {e}")
        
        # Reset interrupt flag after emergency actions
        self.interrupt_requested = False
    
    def process_command_queue(self):
        """Process the command queue"""
        if self.interrupt_requested or self.is_processing:
            return
            
        try:
            self.is_processing = True
            
            if not self.command_queue.empty():
                command = self.command_queue.get_nowait()
                try:
                    self.serial_comm.send_command(command)
                    print(f"Command sent to Arduino: {command}")
                except Exception as e:
                    print(f"Error sending command '{command}': {e}")
        except Exception as e:
            print(f"Error processing command queue: {e}")
        finally:
            self.is_processing = False


class MainWindow(QtWidgets.QMainWindow):
    # Define a high-priority emergency stop signal
    emergency_signal = pyqtSignal()
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Load the UI file directly
        uic.loadUi('GUIver5.1.ui', self)
        
        # Connect the emergency signal
        self.emergency_signal.connect(self.perform_emergency_stop, Qt.QueuedConnection)
        
        # Setup stdout redirection to logMessageLine
        self.stdout_redirector = OutputStreamRedirector(self.logMessageLine)
        sys.stdout = self.stdout_redirector
        
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
            arduino_comm = SerialCommunicator(port='/dev/ttyACM0', baudrate=9600, timeout=1)
            self.arduino = SafeSerialCommunicator(arduino_comm)
            print("✅ Arduino connected successfully")
        except Exception as e:
            print(f"Error initializing Arduino: {str(e)}")
            self.arduino = None
        
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
        camera_index = 2
        if not self.is_webcam_open_first_time:
            camera_index = 2
            time.sleep(1)
            self.is_webcam_open_first_time = True
        
        # Start the webcam thread
        if self.webcam_thread.start_capture(camera_index):
            self.is_webcam_open = True
            print("✅ Webcam started ✅")
        else:
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", 
                                        "Could not open webcam. Click View button again.")

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
        """Immediately stop all operations - invoked by the emergency signal"""
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
        
        # Interrupt Arduino operations and clear command queue
        if self.arduino:
            self.arduino.interrupt()
        
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
                # Rectangle shape
                rect_width = 400 
                rect_height = 120 
                rect_x = 120
                rect_y = 265
                
                # Crop the frame to the size of the red rectangle
                cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]
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
                        self.confirm_finish()
                else: # Successfully extract text 
                    print(f"OCR Result: {result_number}")

                    kPa = result_number[0]
                    Cal = result_number[1]

                    self.kpaNumber.setText(str(kPa))
                    self.calNumber.setText(str(Cal))

                    if kPa == 0:
                        self.lowVoltageTestResult.setText('OK')
                        self.arduino.send_command('PRESS_P')
                        self.finish()
                    else:
                        self.lowVoltageTestResult.setText('ERROR')
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
            self.startButton.setText("STOP")
            # self.startButton.setStyleSheet("background-color: rgb(204, 0, 0);")
            self.is_running = True            
            self.start()  
        else: 
            return
    
    def start(self):
        # Reset UI elements
        self.calNumber.setText('--')
        self.kpaNumber.setText('--')
        self.lowVoltageTestResult.setText('--') 
        self.highVoltageTestResult.setText('--')
        
        if not self.is_webcam_open:
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "ERROR: Webcam not open")
            return
            
        if not self.arduino:
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Arduino not connected")
            return
        
        print("Starting sequence - sending PUMP_SEQ command")
        
        # Send the PUMP_SEQ command via the safe communicator
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
                    
                    # Take snapshot to capture the results
                    QTimer.singleShot(500, self.snapshot)  # Small delay to let everything settle
                
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
                rect_width = 400 
                rect_height = 120 
                rect_x = 120
                rect_y = 265
                cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]
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
                    
                    # Send command via the safe communicator
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

        # Calculate the size and position for the hollow rectangle
        rect_width = 400 
        rect_height = 120 
        rect_x = 120
        rect_y = 265
        
        # Draw the hollow rectangle
        painter.drawRect(rect_x, rect_y, rect_width, rect_height)
        
        # End painting
        painter.end()
        
        # Update the label with the modified pixmap
        self.webcamFrame.setPixmap(pixmap)

    def confirm_finish(self): 
        # Check if we're still running before showing dialog
        if not self.is_running:
            return
            
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())