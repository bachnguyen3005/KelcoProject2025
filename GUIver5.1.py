from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QObject, QEventLoop
from PyQt5.QtGui import QImage, QPixmap, QPainter, QMovie
from ocr import OCRProcessor
from utils_thread import SerialCommunicator
import serial
import sys
from datetime import datetime
import time
import cv2

class CameraWorker(QThread):
    """Worker thread for continuous camera monitoring and image capture on request"""
    image_captured_signal = pyqtSignal(str)
    
    def __init__(self, cap, capture_path, rect_dimensions):
        super().__init__()
        self.cap = cap
        self.capture_path = capture_path
        self.rect_dimensions = rect_dimensions  # (x, y, width, height)
        self.running = True
        self.capture_requested = False
        self.capture_mode = None  # To determine what type of capture (lock_status or numbers)
        
    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret and self.capture_requested:
                x, y, w, h = self.rect_dimensions
                cropped_frame = frame[y:y+h, x:x+w]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if self.capture_mode == 'lock_status':
                    image_filename = f"{self.capture_path}/LOCK2UNLOCK{timestamp}.jpg"
                else:  # Default or 'numbers' mode
                    image_filename = f"{self.capture_path}/processed_snapshot_simple{timestamp}.jpg"
                    
                cv2.imwrite(image_filename, cropped_frame)
                self.capture_requested = False
                self.image_captured_signal.emit(image_filename)
            
            # Small sleep to prevent high CPU usage
            time.sleep(0.05)
    
    def request_capture(self, mode='numbers'):
        """Request an image capture with the specified mode"""
        self.capture_mode = mode
        self.capture_requested = True
        
    def stop(self):
        """Stop the camera worker thread"""
        self.running = False

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

# Worker thread for Arduino interactions
class ArduinoWorker(QThread):
    response_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    
    def __init__(self, serial_communicator, sequence_type):
        super().__init__()
        self.serial_communicator = serial_communicator
        self.sequence_type = sequence_type
        self.running = True
        self.mutex = QtCore.QMutex()
        
        # Connect to the serial communicator's signals
        self.serial_communicator.response_signal.connect(self.handle_response)
        
        # Track sequence state
        self.current_step = 0
        self.sequence_steps = []
        self.waiting_for_response = False
        self.expected_response = None
    
    def run(self):
        """Execute the sequence"""
        try:
            # Define the sequence steps based on sequence_type
            self.define_sequence()
            
            # Start the sequence
            self.execute_next_step()
            
            # Main sequence management loop
            while self.running and self.current_step < len(self.sequence_steps):
                # Check if we're waiting for a response
                if not self.waiting_for_response:
                    # Execute the next step if we're not waiting
                    self.execute_next_step()
                
                # Prevent high CPU usage
                QtCore.QThread.msleep(50)
            
            if self.running:  # Only if we weren't stopped
                self.finished_signal.emit()
                
        except Exception as e:
            print(f"Error in sequence worker: {str(e)}")
            self.finished_signal.emit()
    
    def define_sequence(self):
        """Define the sequence steps based on sequence_type"""
        if self.sequence_type == 'PUMP_SEQ':
            self.sequence_steps = [
                {'command': 'PUMP_SEQ', 'wait_for': 'DONE'},
                # No more steps - after DONE response, camera capture happens
            ]
        elif self.sequence_type == 'LOCKED_SEQUENCE':
            self.sequence_steps = [
                {'command': 'LOCKED_SEQUENCE', 'wait_for': 'SEQUENCE_COMPLETE'}
            ]
        elif self.sequence_type == 'UNLOCKED_SEQUENCE':
            self.sequence_steps = [
                {'command': 'UNLOCKED_SEQUENCE', 'wait_for': 'SEQUENCE_COMPLETE'}
            ]
        # Add other sequences as needed
    
    def execute_next_step(self):
        """Execute the next step in the sequence"""
        if self.current_step >= len(self.sequence_steps):
            return
            
        step = self.sequence_steps[self.current_step]
        
        # Send the command to the serial communicator
        self.serial_communicator.send_command(step['command'])
        
        # If we need to wait for a response, set the waiting flag
        if 'wait_for' in step:
            self.waiting_for_response = True
            self.expected_response = step['wait_for']
        else:
            # If no response needed, move to next step
            self.current_step += 1
    
    def handle_response(self, response):
        """Handle responses from the serial communicator"""
        # First forward the response to any listeners
        self.response_signal.emit(response)
        
        # Check if this is the response we're waiting for
        if self.waiting_for_response and response == self.expected_response:
            self.waiting_for_response = False
            self.current_step += 1
            
            # Special case: when we get SEQUENCE_COMPLETE, we're done
            if response == 'SEQUENCE_COMPLETE':
                self.running = False
                self.finished_signal.emit()
    
    def stop(self):
        """Stop the sequence and send stop command"""
        self.mutex.lock()
        self.running = False
        self.mutex.unlock()
        
        # Send stop command via the serial communicator
        self.serial_communicator.emergency_stop()


# Worker thread for OCR processing
class OCRWorker(QThread):
    result_signal = pyqtSignal(object)
    
    def __init__(self, ocr_processor, image_path, mode='numbers'):
        super().__init__()
        self.ocr_processor = ocr_processor
        self.image_path = image_path
        self.mode = mode
        
    def run(self):
        try:
            if self.mode == 'numbers':
                result = self.ocr_processor.extract_numbers(self.image_path)
            else:  # lock status
                result = self.ocr_processor.get_lock_status(self.image_path)
                
            self.result_signal.emit(result)
        except Exception as e:
            print(f"Error in OCR worker: {str(e)}")
            self.result_signal.emit("ERROR")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Load the UI file directly
        uic.loadUi('GUIver5.1.ui', self)
        
        # Setup stdout redirection to logMessageLine
        self.stdout_redirector = OutputStreamRedirector(self.logMessageLine)
        sys.stdout = self.stdout_redirector
        
        # Now you can access UI elements directly
        self.populate_model_list()
        
        self.is_webcam_open = False
        self.is_webcam_open_first_time = False
        self.is_running = False  # Track the current state (GO/STOP)
        self.timers = []  # List to store all the timers
        self.workers = []  # List to track all worker threads
        self.camera_worker = None  # Will be initialized when webcam starts
    
        
        try:
            self.serial_communicator = SerialCommunicator(port='/dev/ttyACM0', baudrate=9600, timeout=1)
            self.serial_communicator.error_signal.connect(self.handle_arduino_error)
            self.serial_communicator.connected_signal.connect(self.handle_arduino_connection)
            self.serial_communicator.start()
        except Exception as e:
            print(f"Error initializing serial communicator: {str(e)}")
            self.serial_communicator = None
        
        # Connect signals
        self.startButton.clicked.connect(self.toggle_Go_Stop)
        self.viewButton.clicked.connect(self.start_webcam)
        self.closeButton.clicked.connect(self.stop_webcam)
        self.Snap.clicked.connect(self.snapshot)
        
        # Initialize GUI state
        self.startButton.setText("GO")
        self.startButton.setStyleSheet("background-color: rgb(138, 226, 52);")
        
        # Initialize components
        QTimer.singleShot(0, self.initialize_ocr)
        QTimer.singleShot(0, self.start_webcam)
        
    def __del__(self):
        # Restore original stdout when the application is closed
        sys.stdout = sys.__stdout__
        
    def populate_model_list(self):
        # Add items to the combo box
        models = ["F60", "E30", "IPG20", "F29"]
        self.modelList.addItems(models)
        
    def start_webcam(self):
        self.cap = cv2.VideoCapture(2)   
        if self.cap.isOpened():
            self.is_webcam_open = True
            self.timer = QTimer()  # Set up timer for updating the frame
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)  # Update frame every 30 ms
            self.timers.append(self.timer)  # Add to the timer list for cleanup
            
            # Initialize and start the camera worker
            capture_path = "/home/dinh/Documents/PlatformIO/Projects/kelco_test_001/SnapShotImages"
            rect_dimensions = (130, 255, 400, 120)  # x, y, width, height
            self.camera_worker = CameraWorker(self.cap, capture_path, rect_dimensions)
            self.camera_worker.image_captured_signal.connect(self.process_captured_image)
            self.workers.append(self.camera_worker)
            self.camera_worker.start()
            
            print("Webcam started")
        else: 
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Could not open webcam. Click View button again.")
            return

    def stop_webcam(self):
        if self.is_webcam_open:
            for timer in self.timers:
                if timer.isActive():
                    timer.stop()
            self.timers.clear()
            
            # Stop camera worker if it exists
            if self.camera_worker and self.camera_worker.isRunning():
                self.camera_worker.stop()
                self.camera_worker.wait()  # Wait for thread to finish
            
            if hasattr(self, 'cap'):
                self.cap.release()
            
            self.is_webcam_open = False
            self.webcamFrame.clear()
            print("Webcam stopped")
    
    def toggle_Go_Stop(self):
        """Handle the GO/STOP button click with immediate visual feedback"""
        print(f"Toggle button pressed, current state: {'Running' if self.is_running else 'Stopped'}")
        
        # If we're currently running, prioritize the stop operation
        if self.is_running:
            # Provide immediate visual feedback
            self.startButton.setText("Stopping...")
            self.startButton.setStyleSheet("background-color: orange;")
            
            # Process events to update the UI immediately
            QtWidgets.QApplication.instance().processEvents()
            
            # Perform the emergency stop
            self.emergency_stop()
        else:
            # Start process with confirmation dialog
            self.confirm_start()
        
    def emergency_stop(self):
        """Immediately stop all operations without blocking the UI"""
        print("EMERGENCY STOP activated")
        
        # First, set flags to indicate we're stopping
        self.is_running = False
        
        # Visual feedback immediately
        self.startButton.setText("GO")
        # self.startButton.setStyleSheet("background-color: rgb(138, 226, 52);")
        
        # Process events to update UI immediately
        QtWidgets.QApplication.instance().processEvents()
        
        # Send emergency stop to Arduino FIRST - most critical action
        if self.serial_communicator and self.serial_communicator.isRunning():
            try:
                self.serial_communicator.emergency_stop()
                print("Emergency stop command sent to Arduino")
            except Exception as e:
                print(f"Error sending stop command: {str(e)}")
        
        # Stop worker threads in background
        for worker in self.workers[:]:
            if worker.isRunning():
                if isinstance(worker, ArduinoWorker):
                    worker.stop()  # This will also trigger emergency stop on serial
                elif isinstance(worker, CameraWorker):
                    worker.stop()
                # Don't wait for threads to finish here - just set their stop flags
        
        # Stop all timers
        for timer in self.timers:
            if timer.isActive():
                timer.stop()
        self.timers.clear()
        
        # Cancel any ongoing message boxes
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if isinstance(widget, QtWidgets.QMessageBox):
                widget.close()
        
        # Schedule cleanup to happen in the background
        QtCore.QTimer.singleShot(500, self._cleanup_after_stop)
        
        # Process events again for immediate UI update
        QtWidgets.QApplication.instance().processEvents()
        
        print("System stopped")

    def _cleanup_after_stop(self):
        """Clean up resources after emergency stop"""
        # Wait for worker threads to finish properly
        for worker in self.workers[:]:
            if worker.isRunning():
                worker.wait(100)  # Short timeout to avoid blocking
            self.workers.remove(worker)
        
        # Final UI updates
        self.logMessageLine.setText("System stopped")
    
    def snapshot(self):
        if not self.is_running:
            print("System not running, snapshot cancelled")
            return
        
        # Request camera to capture numbers
        print("Requesting numbers capture...")
        if self.camera_worker and self.camera_worker.isRunning():
            self.camera_worker.request_capture(mode='numbers')
        else:
            print("Camera worker not running, cannot capture image")
    
    def handle_ocr_result(self, result_number):
        # Check if we're still running
        if not self.is_running:
            return
            
        print("OCR processing completed")
        
        if result_number == "ERROR":
            # Only show message box if still running
            if self.is_running:
                QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Error")
                # self.confirm_finish()
        else: # Successfully extract text 
            print(f"OCR Result: {result_number}")

            kPa = result_number[0]
            Cal = result_number[1]

            self.kpaNumber.setText(str(kPa))
            self.calNumber.setText(str(Cal))

            if kPa == 0:
                self.lowVoltageTestResult.setText('OK')
                # self.confirm_finish()
                #send to arduino 'confirm finish low voltage'
            else:
                self.lowVoltageTestResult.setText('ERROR')
                # self.confirm_finish()
                #send to arduino 'confirm finish low voltage'
                
    def initialize_ocr(self): 
        self.ocr_processor = OCRProcessor()
        print("OCR system initialized")
    
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
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "ERROR")
            return
            
        if not self.serial_communicator or not self.serial_communicator.isRunning():
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Serial communicator not connected")
            return
        
        print("Starting sequence - creating sequence worker for PUMP_SEQ")
        
        # Create and start a sequence worker
        self.arduino_worker = ArduinoWorker(self.serial_communicator, 'PUMP_SEQ')
        self.arduino_worker.response_signal.connect(self.handle_arduino_response)
        self.arduino_worker.finished_signal.connect(self.on_arduino_finished)
        self.workers.append(self.arduino_worker)
        self.arduino_worker.start()

    def handle_arduino_response(self, response):
        # Process arduino responses
        print(f"Received response: {response}")
        
        # Check if we're still running
        if not self.is_running:
            return
            
        if response == "DONE":
            # Request camera to capture lock status
            print("Requesting lock status capture...")
            if self.camera_worker and self.camera_worker.isRunning():
                self.camera_worker.request_capture(mode='lock_status')
            else:
                print("Camera worker not running, cannot capture image")
    
    def on_arduino_finished(self):
        print("Arduino sequence finished")
        # Remove worker from list when done
        for worker in self.workers[:]:
            if not worker.isRunning():
                self.workers.remove(worker)
    
    def handle_lock_status(self, extracted_text):
        # Check if we're still running
        if not self.is_running:
            return
            
        print(f"Lock status: {extracted_text}")
        
        if extracted_text == "LOCKED" or extracted_text == "UNLOCKED":
            # Start the appropriate sequence in a thread
            self.sequence_worker = ArduinoWorker(
                self.serial_communicator, 
                'LOCKED_SEQUENCE' if extracted_text == "LOCKED" else 'UNLOCKED_SEQUENCE'
            )
            self.sequence_worker.response_signal.connect(self.handle_sequence_response)
            self.sequence_worker.finished_signal.connect(self.on_sequence_finished)
            self.workers.append(self.sequence_worker)
            self.sequence_worker.start()
            
            print(f"Starting {extracted_text} sequence")
        else:
            # Only show message if still running
            if self.is_running:
                QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", 
                                          "Could not recognize lock status. Please try again.")
                # self.confirm_finish()
    
    def handle_sequence_response(self, response):
        # Log all responses from the sequence
        print(f"Sequence response: {response}")
        
        # Update log message line
        self.logMessageLine.setText(response)
        
        # Process special responses
        if response == "SEQUENCE_COMPLETE":
            # Take snapshot to capture final values
            self.snapshot()
    
    def on_sequence_finished(self):
        print("Sequence completed")
        # Remove worker from list when done
        for worker in self.workers[:]:
            if not worker.isRunning():
                self.workers.remove(worker)
        
    def finish(self):
        # Only reset if we're still running
        if self.is_running:
            self.startButton.setText("GO")
            self.is_running = False
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
        rect_height = 130 
        rect_x = 120
        rect_y = 255
        
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

    def process_captured_image(self, image_filename):
        """Process the image captured by the camera worker"""
        # Check if we're still running
        if not self.is_running:
            return
        
        # Determine which type of processing to do based on the filename
        if "LOCK2UNLOCK" in image_filename:
            print("Processing lock status image...")
            # Process lock status
            self.lock_ocr_worker = OCRWorker(self.ocr_processor, image_filename, 'lock_status')
            self.lock_ocr_worker.result_signal.connect(self.handle_lock_status)
            self.workers.append(self.lock_ocr_worker)
            self.lock_ocr_worker.start()
        else:
            print("Processing OCR for numbers...")
            # Process numbers
            self.ocr_worker = OCRWorker(self.ocr_processor, image_filename, 'numbers')
            self.ocr_worker.result_signal.connect(self.handle_ocr_result)
            self.workers.append(self.ocr_worker)
            self.ocr_worker.start()

    def handle_arduino_error(self, error_message):
        """Handle Arduino communication errors"""
        print(f"Arduino error: {error_message}")
        # Show error message or update UI if needed
        if self.is_running:
            # If error is serious, may want to stop operations
            QtWidgets.QMessageBox.warning(self.centralwidget, "Arduino Error", error_message)

    def handle_arduino_connection(self, connected):
        """Handle Arduino connection status changes"""
        if connected:
            print("Arduino connected successfully")
        else:
            print("Arduino disconnected")
            if self.is_running:
                # If we lose connection during operation, stop everything
                self.emergency_stop()
                QtWidgets.QMessageBox.warning(self.centralwidget, "Connection Lost", 
                                        "Arduino connection lost. Operations stopped.")



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())