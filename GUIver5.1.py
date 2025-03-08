from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QObject, QEventLoop
from PyQt5.QtGui import QImage, QPixmap, QPainter, QMovie
from ocr import OCRProcessor
from utils import SerialCommunicator
import serial
import sys
from datetime import datetime
import time
import cv2


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
    
    def __init__(self, arduino, command):
        super().__init__()
        self.arduino = arduino
        self.command = command
        self.running = True
        
    def run(self):
        try:
            # Send the command to Arduino
            self.arduino.send_command(self.command)
            
            # Monitor for responses
            while self.running:
                response = self.arduino.read_command()
                if response:
                    self.response_signal.emit(response)
                    
                    # If we get SEQUENCE_COMPLETE, we're done
                    if response == "SEQUENCE_COMPLETE":
                        break
                        
                # Small sleep to prevent high CPU usage
                time.sleep(0.05)
                
            self.finished_signal.emit()
            
        except Exception as e:
            print(f"Error in Arduino worker: {str(e)}")
            self.finished_signal.emit()
    
    def stop(self):
        self.running = False
        # Send stop command to Arduino
        try:
            self.arduino.send_command('STOP')
        except:
            pass


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
        
        try:
            self.arduino = SerialCommunicator(port='/dev/ttyACM0', baudrate=9600, timeout=1)
        except Exception as e:
            print(f"Error initializing Arduino: {str(e)}")
            self.arduino = None
        
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
            self.timers.append(self.timer)  # Add to the timer list for cleanup
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
            
            if hasattr(self, 'cap'):
                self.cap.release()
            
            self.is_webcam_open = False
            self.webcamFrame.clear()
            print("Webcam stopped")
    
    def toggle_Go_Stop(self):
        print(f"Toggle button pressed, current state: {'Running' if self.is_running else 'Stopped'}")
        if not self.is_running:
            # Start the process
            self.confirm_start()
        else:
            # Stop everything immediately
            self.emergency_stop()
    
    def emergency_stop(self):
        """Immediately stop all operations"""
        print("EMERGENCY STOP activated")
        
        # First, set flags to indicate we're stopping
        self.is_running = False
        
        # Stop all worker threads
        for worker in self.workers:
            if worker.isRunning():
                if isinstance(worker, ArduinoWorker):
                    worker.stop()  # Special method for Arduino workers
                worker.quit()
                worker.wait(500)  # Wait up to 500ms for thread to finish
        
        self.workers.clear()
        
        # Stop all timers
        for timer in self.timers:
            if timer.isActive():
                timer.stop()
        self.timers.clear()
        
        # Send stop command directly, just to be sure
        if self.arduino:
            try:
                self.arduino.send_command('STOP')
                print("Stop command sent to Arduino")
            except Exception as e:
                print(f"Error sending stop command: {str(e)}")
        
        # Reset UI elements
        self.startButton.setText("GO")
        
        # Cancel any ongoing message boxes
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if isinstance(widget, QtWidgets.QMessageBox):
                widget.close()
        
        # Process events to ensure UI updates
        QApplication = QtWidgets.QApplication.instance()
        QApplication.processEvents()
        
        print("System stopped")
    
    def snapshot(self):
        if not self.is_running:
            print("System not running, snapshot cancelled")
            return
            
        ret, frame = self.cap.read()
        if ret:
            #Rectangle shape
            rect_width = 400 
            rect_height = 120 
            rect_x = 120
            rect_y = 265
            # Crop the frame to the size of the red rectangle
            cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"/home/dinh/Documents/PlatformIO/Projects/kelco_test_001/SnapShotImages/processed_snapshot_simple{timestamp}.jpg"                 
            # Save the processed image for OCRvoid loop(){  
            cv2.imwrite(image_filename, cropped_frame)
            
            # Check if we're still running before proceeding with OCR
            if not self.is_running:
                return
                
            # Create and start OCR worker thread
            self.ocr_worker = OCRWorker(self.ocr_processor, image_filename, 'numbers')
            self.ocr_worker.result_signal.connect(self.handle_ocr_result)
            self.workers.append(self.ocr_worker)
            self.ocr_worker.start()
            
            # Update log message
            print("Processing OCR...")
    
    def handle_ocr_result(self, result_number):
        # Check if we're still running
        if not self.is_running:
            return
            
        print("OCR processing completed")
        
        if result_number == "ERROR":
            # Only show message box if still running
            if self.is_running:
                QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Error")
                self.confirm_finish()
        else: # Successfully extract text 
            print(f"OCR Result: {result_number}")

            kPa = result_number[0]
            Cal = result_number[1]

            self.kpaNumber.setText(str(kPa))
            self.calNumber.setText(str(Cal))

            if kPa == 0:
                self.lowVoltageTestResult.setText('OK')
                self.confirm_finish()
                #send to arduino 'confirm finish low voltage'
            else:
                self.lowVoltageTestResult.setText('ERROR')
                self.confirm_finish()
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
            self.startButton.setStyleSheet("background-color: rgb(204, 0, 0);")
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
            
        if not self.arduino:
            QtWidgets.QMessageBox.warning(self.centralwidget, "Warning", "Arduino not connected")
            return
        
        print("Starting sequence - sending PUMP_SEQ command")
        
        # Start Arduino worker in a thread
        self.arduino_worker = ArduinoWorker(self.arduino, 'PUMP_SEQ')
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
            # Take snapshot of lock status
            self.capture_lock_status()
    
    def on_arduino_finished(self):
        print("Arduino sequence finished")
        # Remove worker from list when done
        for worker in self.workers[:]:
            if not worker.isRunning():
                self.workers.remove(worker)
    
    def capture_lock_status(self):
        # Check if we're still running
        if not self.is_running:
            return
            
        ret, frame = self.cap.read()
        if ret:
            rect_width = 400 
            rect_height = 120 
            rect_x = 120
            rect_y = 265
            cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"/home/dinh/Documents/PlatformIO/Projects/kelco_test_001/SnapShotImages/LOCK2UNLOCK{timestamp}.jpg"
            cv2.imwrite(image_filename, cropped_frame) 
            
            # Process lock status in a thread
            self.lock_ocr_worker = OCRWorker(self.ocr_processor, image_filename, 'lock_status')
            self.lock_ocr_worker.result_signal.connect(self.handle_lock_status)
            self.workers.append(self.lock_ocr_worker)
            self.lock_ocr_worker.start()
            
            print("Determining lock status...")
    
    def handle_lock_status(self, extracted_text):
        # Check if we're still running
        if not self.is_running:
            return
            
        print(f"Lock status: {extracted_text}")
        
        if extracted_text == "LOCKED" or extracted_text == "UNLOCKED":
            # Start the appropriate sequence in a thread
            self.sequence_worker = ArduinoWorker(
                self.arduino, 
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
                self.confirm_finish()
    
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


# No longer need the ArduinoStateMachine class as its functionality is now handled by threads

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())