import cv2
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout,
                             QFrame, QSizePolicy, QTextEdit, QComboBox, QLCDNumber)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont, QPainter
from ocr import OCRProcessor
from utils import SerialCommunicator
import serial
import serial.tools.list_ports
import time 
from playsound import playsound
import threading
from datetime import datetime
class ActuatorControl(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize OCR Processor and Serial Communicator
        self.ocr_processor = OCRProcessor()

        # self.arduino = SerialCommunicator(port='/dev/ttyUSB1', baudrate=115200, timeout=1)

        # self.arduino = SerialCommunicator(port='/dev/ttyACM0', baudrate=9600, timeout=1)
      
        # Create a variable for the currently selected webcam
        self.selected_camera_index = 0

        # Set up the GUI layout
        self.initUI()

        # Set up a timer to update the webcam frame
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def initUI(self):
        self.setWindowTitle('Actuator Control with Webcam and OCR')
        self.showMaximized()  # Maximize the window on startup

        # Create a main vertical layout
        main_layout = QVBoxLayout()

        # Title frame
        title_frame = QFrame(self)
        title_frame.setStyleSheet("background-color: purple;")
        title_layout = QVBoxLayout(title_frame)
        title_label = QLabel("Actuator Control System")
        title_label.setStyleSheet("color: white;")
        title_label.setFont(QFont('Arial', 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        title_frame.setLayout(title_layout)
        main_layout.addWidget(title_frame)

        # Camera selection dropdown and button
        camera_selection_layout = QHBoxLayout()
        self.camera_dropdown = QComboBox(self)
        self.update_camera_list()  # Populate the dropdown with available cameras
        camera_selection_layout.addWidget(self.camera_dropdown)

        self.connect_camera_button = QPushButton('Connect to Camera', self)
        self.connect_camera_button.clicked.connect(self.connect_to_selected_camera)
        camera_selection_layout.addWidget(self.connect_camera_button)

        main_layout.addLayout(camera_selection_layout)


        # Frame layout for webcam and captured image
        frame_layout = QHBoxLayout()

        # Webcam frame
        self.webcam_frame = QFrame(self)
        self.webcam_frame.setStyleSheet("""
            QFrame {
                color: black;
                border-style: outset;
                border: 3px solid black;  /* Black border with 2px thickness */
                border-radius: 5px;       /* Optional: Rounded corners */
                background-color: white;  /* Optional: Set background color */
            }
        """)
        self.webcam_layout = QVBoxLayout(self.webcam_frame)
        webcam_title_label = QLabel("Webcam Feed")
        webcam_title_label.setStyleSheet("""
            QLabel {
                border-style: outset;
                font: bold 25px;                   /* Set the font size */
                border: 3px solid red;             /* Create a red border */
                padding: 10px;                     /* Add padding inside the border */
                border-radius: 5px;                /* Optional: Add rounded corners */
                background-color: white;           /* Optional: Set background color */
            }
        """)
        webcam_title_label.setFont(QFont('Arial', 18))
        webcam_title_label.setAlignment(Qt.AlignCenter)
        self.webcam_layout.addWidget(webcam_title_label)
        self.webcam_label = QLabel(self)
        self.webcam_layout.addWidget(self.webcam_label)
        self.webcam_frame.setLayout(self.webcam_layout)
        self.webcam_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        frame_layout.addWidget(self.webcam_frame)

        # Captured image frame
        self.captured_frame = QFrame(self)
        self.captured_frame.setStyleSheet("""
            QFrame {
                color: black;
                border-style: outset;
                border: 3px solid black;  /* Black border with 2px thickness */
                border-radius: 5px;       /* Optional: Rounded corners */
                background-color: white;  /* Optional: Set background color */
            }
        """)
        self.captured_layout = QVBoxLayout(self.captured_frame)
        self.captured_label = QLabel("Text detected image")
        self.captured_label.setStyleSheet("""
            QLabel {
                border-style: outset;
                font: bold 25px;                   /* Set the font size */
                border: 3px solid red;             /* Create a red border */
                padding: 10px;                     /* Add padding inside the border */
                border-radius: 5px;                /* Optional: Add rounded corners */
                background-color: white;           /* Optional: Set background color */
            }
        """)
        self.captured_label.setAlignment(Qt.AlignCenter)
        self.captured_layout.addWidget(self.captured_label)
        self.captured_frame.setLayout(self.captured_layout)
        self.captured_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        frame_layout.addWidget(self.captured_frame)

        main_layout.addLayout(frame_layout)

        # # Text box for OCR output
        # self.text_box = QTextEdit("Extracted text")
        # bold_font = QFont('Arial', 20)
        # bold_font.setBold(True)
        # self.text_box.setFont(bold_font)
        # main_layout.addWidget(self.text_box)



        # LCD display section
        lcd_layout = QHBoxLayout()

        # Kpa display
        kpa_layout = QVBoxLayout()
        self.kpa_label = QLabel("Kpa")
        self.kpa_label.setAlignment(Qt.AlignCenter)
        self.kpa_label.setFont(QFont('Arial', 40, QFont.Bold))
        kpa_layout.addWidget(self.kpa_label)

        self.kpa_lcd = QLCDNumber(self)
        self.kpa_lcd.setDigitCount(6)
        self.kpa_lcd.setStyleSheet("background-color: yellow; color: green;")
        kpa_layout.addWidget(self.kpa_lcd)
        lcd_layout.addLayout(kpa_layout)

        # Cal display
        cal_layout = QVBoxLayout()
        self.cal_label = QLabel("Cal")
        self.cal_label.setAlignment(Qt.AlignCenter)
        self.cal_label.setFont(QFont('Arial', 40, QFont.Bold))
        cal_layout.addWidget(self.cal_label)

        self.cal_lcd = QLCDNumber(self)
        self.cal_lcd.setDigitCount(6)
        self.cal_lcd.setStyleSheet("background-color: yellow; color: green;")
        cal_layout.addWidget(self.cal_lcd)
        lcd_layout.addLayout(cal_layout)

        main_layout.addLayout(lcd_layout)


        # Buttons
        button_layout = QHBoxLayout()   

        button_layout_1 = QVBoxLayout()
        self.extend_button = QPushButton('Extend Actuator', self)
        self.extend_button.clicked.connect(self.extend_actuator)
        self.extend_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.extend_button.setStyleSheet("font: bold 20px; background-color: green; color: black; padding: 10px 20px;")
        button_layout_1.addWidget(self.extend_button)

        self.retract_button = QPushButton('Retract Actuator', self)
        self.retract_button.clicked.connect(self.retract_actuator)
        self.retract_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.retract_button.setStyleSheet("font: bold 20px; background-color: red; color: black; padding: 10px 20px;")
        button_layout_1.addWidget(self.retract_button)

        self.stop_button_1 = QPushButton('Stop Actuator 1', self)
        self.stop_button_1.clicked.connect(self.stop_actuator)
        self.stop_button_1.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.stop_button_1.setStyleSheet("font: bold 20px; background-color: orange; color: black; padding: 10px 20px;")
        button_layout_1.addWidget(self.stop_button_1)


        button_layout.addLayout(button_layout_1)

        button_layout_2 = QVBoxLayout()
        self.extend_button_2 = QPushButton('LOCKED2UNLOCKED', self) #LOCK2UNLOCKED button 
        self.extend_button_2.clicked.connect(self.unlock_mode)
        self.extend_button_2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.extend_button_2.setStyleSheet("font: bold 20px; background-color: red; color: black; padding: 10px 20px;")
        button_layout_2.addWidget(self.extend_button_2)

        self.retract_button_2 = QPushButton('PUMP ON', self)    #Pump ON button 
        self.retract_button_2.clicked.connect(self.pumpON)
        self.retract_button_2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.retract_button_2.setStyleSheet("font: bold 20px; background-color: red; color: black; padding: 10px 20px;")
        button_layout_2.addWidget(self.retract_button_2)

        self.stop_button_2 = QPushButton('PUMP OFF', self)  #Pump OFF button 
        self.stop_button_2.clicked.connect(self.pumpOFF)
        self.stop_button_2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.stop_button_2.setStyleSheet("font: bold 20px; background-color: orange; color: black; padding: 10px 20px;")
        button_layout_2.addWidget(self.stop_button_2)

        button_layout.addLayout(button_layout_2)

        button_layout_3 = QVBoxLayout()
        self.extend_button_3 = QPushButton('Retract Actuator 2 and 3', self)    #Retract Actuator 2 and 3 Button 
        self.extend_button_3.clicked.connect(self.retract_acutator_23)
        self.extend_button_3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.extend_button_3.setStyleSheet("font: bold 20px; background-color: red; color: black; padding: 10px 20px;")
        button_layout_3.addWidget(self.extend_button_3)

        self.retract_button_3 = QPushButton('Retract Actuator 3', self)
        self.retract_button_3.clicked.connect(self.retract_actuator_3)
        self.retract_button_3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.retract_button_3.setStyleSheet("font: bold 20px; background-color: red; color: black; padding: 10px 20px;")
        button_layout_3.addWidget(self.retract_button_3)

        self.stop_button_3 = QPushButton('Stop Actuator 3', self)
        self.stop_button_3.clicked.connect(self.stop_actuator_3)
        self.stop_button_3.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.stop_button_3.setStyleSheet("font: bold 20px; background-color: red; color: black; padding: 10px 20px;")
        button_layout_3.addWidget(self.stop_button_3)
        button_layout.addLayout(button_layout_3)

        button_layout_4 = QVBoxLayout()
        self.extend_button_4 = QPushButton('Extend Actuator 4', self)
        self.extend_button_4.clicked.connect(self.extend_actuator_4)
        self.extend_button_4.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.extend_button_4.setStyleSheet("font: bold 20px; background-color: red; color: black; padding: 10px 20px;")
        button_layout_4.addWidget(self.extend_button_4)

        self.retract_button_4 = QPushButton('CLOSE AIR', self) #Valve ON button 
        self.retract_button_4.clicked.connect(self.closeAir)
        self.retract_button_4.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.retract_button_4.setStyleSheet("font: bold 20px; background-color: red; color: black; padding: 10px 20px;")
        button_layout_4.addWidget(self.retract_button_4)

        self.stop_button_4 = QPushButton('OPEN AIR', self) #Valve OFF button 
        self.stop_button_4.clicked.connect(self.openAir)
        self.stop_button_4.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.stop_button_4.setStyleSheet("font: bold 20px; background-color: red; color: black; padding: 10px 20px;")
        button_layout_4.addWidget(self.stop_button_4)

        button_layout.addLayout(button_layout_4)

        #Capture button layout 
        capture_button_layout = QVBoxLayout()
        self.capture_button = QPushButton('Capture Image and OCR', self)
        self.capture_button.clicked.connect(self.snapshot)
        self.capture_button.clicked.connect(self.display_captured_image_msg)
        self.capture_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.capture_button.setStyleSheet("font: bold 20px; background-color: blue; color: black; padding: 10px 20px;")
        capture_button_layout.addWidget(self.capture_button)

        button_layout.addLayout(capture_button_layout)

        main_layout.addLayout(button_layout)


        #Status label
        self.status_label = QLabel('Status: Idle', self)
        self.status_label.setAlignment(Qt.AlignCenter)  # Center-align the text
        self.status_label.setStyleSheet("""
            QLabel {
                border-style: outset;
                font: bold 25px;                   /* Set the font size */
                border: 3px solid red;             /* Create a red border */
                padding: 10px;                     /* Add padding inside the border */
                border-radius: 5px;                /* Optional: Add rounded corners */
                background-color: white;           /* Optional: Set background color */
            }
        """)
        main_layout.addWidget(self.status_label)

        #Set the main layout
        self.setLayout(main_layout)


    def update_camera_list(self):
        """Update the dropdown with available webcams."""
        self.camera_dropdown.clear()
        available_cameras = self.get_available_cameras()
        for i, cam in enumerate(available_cameras):
            self.camera_dropdown.addItem(f"Camera {cam}")
        print(self.camera_dropdown) #Debugging the number of camrea

    def get_available_cameras(self):
        """List available cameras by checking their indices."""
        available_cameras = []
        for i in range(10):  # Check camera indices 0 to 9
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        return available_cameras

    def connect_to_selected_camera(self):
        """Connect to the selected camera from the dropdown."""
        self.selected_camera_index = self.camera_dropdown.currentIndex()
        if (self.selected_camera_index == 0):
            self.selected_camera_index = 0
            self.cap = cv2.VideoCapture(self.selected_camera_index)

            if self.cap.isOpened():
                self.status_label.setText(f'Status: Connected to Camera {self.selected_camera_index}')
                self.timer.start(10)  # Start capturing frames
            else:
                self.status_label.setText(f'Status: Failed to connect to Camera {self.selected_camera_index}')
        elif self.selected_camera_index == 1: 
            self.selected_camera_index = 2
            self.cap = cv2.VideoCapture(2)

            if self.cap.isOpened():
                self.status_label.setText(f'Status: Connected to Camera {2}')
                self.timer.start(10)  # Start capturing frames
            else:
                self.status_label.setText(f'Status: Failed to connect to Camera {2}')


    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:      
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            qt_pixmap = QPixmap.fromImage(qt_image)
            self.webcam_label.setPixmap(qt_pixmap)
            # self.webcam_label.setScaledContents(True)
            self.webcam_label.setAlignment(Qt.AlignCenter)
            self.draw_red_rectangle()

    def draw_red_rectangle(self):
        # Create a QPixmap to paint on, using the same size as the webcam_label
        pixmap = self.webcam_label.pixmap()
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
        rect_width = 550 #previous 450
        rect_height = 140 
        rect_x = 50 #previous 100
        rect_y = 150
        
        # Draw the hollow rectangle
        painter.drawRect(rect_x, rect_y, rect_width, rect_height)
        
        # End painting
        painter.end()
        
        # Update the label with the modified pixmap
        self.webcam_label.setPixmap(pixmap)


    # def snapshot(self):
    #     ret, frame = self.cap.read()
    #     if ret:
    #         cv2.imwrite("snapshot.jpg", frame)
    #         img_with_text, extracted_text = self.ocr_processor.run_ocr("snapshot.jpg")
    #         h, w, ch = img_with_text.shape
    #         bytes_per_line = ch * w
    #         qt_image = QImage(img_with_text.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #         qt_pixmap = QPixmap.fromImage(qt_image)
    #         # self.captured_label.setScaledContents(True)
    #         self.captured_label.setPixmap(qt_pixmap)
    #         self.captured_label.setAlignment(Qt.AlignCenter)
    #         self.text_box.clear()
    #         self.text_box.setText(extracted_text)
    #     return extracted_text 
    def snapshot(self):
        ret, frame = self.cap.read()
        if ret:
            # Calculate the size and position for the rectangle (same as in draw_red_rectangle)
            rect_width = 450 
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
            img_with_text, extracted_text = self.ocr_processor.run_ocr(image_filename)
            # result = self.ocr_processor.run_ocr_simple(image_filename)
            # print(result[1])
            # result_int = int(result[1])
            # print(result_int)
            # Convert the processed image to QImage
            h, w, ch = img_with_text.shape
            bytes_per_line = ch * w
            qt_image = QImage(img_with_text.data, w, h, bytes_per_line, QImage.Format_RGB888)
            qt_pixmap = QPixmap.fromImage(qt_image)
            
            # Display the processed image in the captured_label
            self.captured_label.setPixmap(qt_pixmap)
            self.captured_label.setAlignment(Qt.AlignCenter)

            # Update the text box with extracted text
            self.text_box.clear()
            self.text_box.setText(extracted_text)  

        

    def extend_actuator(self):
        self.arduino.send_command('E')
        self.status_label.setText('Status: Extending Actuator 1')

    def retract_actuator(self):
        self.arduino.send_command('R')
        self.status_label.setText('Status: Retracting Actuator 1')

    def stop_actuator(self):
        self.arduino.send_command('S')
        self.status_label.setText('Status: Stopping Actuator 1')

    def unlock_mode(self):
        self.arduino.send_command('A')  # Extend the actuator 2 and 3 and pump ON

        self.status_label.setText('Status: Extending Actuator 2 and 3 then wait 2 seconds')
        command2check = "L"  # Check command from arduino
        response = self.arduino.read_command()
        print(response)

        # Timer for after_delay execution
        self.delay_timer = QTimer(self)
        self.delay_timer.setSingleShot(True)  # Make sure the timer fires only once
        self.delay_timer.timeout.connect(lambda: self.after_delay(response, command2check))
        self.delay_timer.start(5000)  # 5-second delay before calling after_delay

    def after_delay(self, response, command2check):
        if response == command2check:
            self.status_label.setText('Status: DONE extending actuator 2 and 3')

            ret, frame = self.cap.read()
            if ret:
                # Process and crop the frame for OCR
                rect_width = 450
                rect_height = 130
                rect_x = 100
                rect_y = 150
                cropped_frame = frame[rect_y:rect_y + rect_height, rect_x:rect_x + rect_width]


                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"SnapShotImages/processed_snapshot_LOCK2UNLOCK{timestamp}.jpg"

                # Save the processed image for OCR
                cv2.imwrite(image_filename, cropped_frame)

                # Perform OCR on the cropped image
                img_with_text, extracted_text = self.ocr_processor.run_ocr(image_filename)

                # Convert the processed image to QImage and display it
                h, w, ch = img_with_text.shape
                bytes_per_line = ch * w
                qt_image = QImage(img_with_text.data, w, h, bytes_per_line, QImage.Format_RGB888)
                qt_pixmap = QPixmap.fromImage(qt_image)

                self.captured_label.setPixmap(qt_pixmap)
                self.captured_label.setAlignment(Qt.AlignCenter)

                # Update the text box with extracted text
                self.text_box.clear()
                self.text_box.setText(extracted_text)

                self.status_label.setText('Status: Finishing detected')

                # Perform further actions based on OCR result
                if extracted_text.strip() == "LOCKED":
                    self.status_label.setText('STATUS: LOCKED MODE')
                    playsound('Sound/LockedModeVer2.mp3')

                    self.stop_timer = QTimer(self)
                    self.stop_timer.setSingleShot(True)
                    self.stop_timer.timeout.connect(lambda: self.arduino.send_command('K'))
                    self.stop_timer.start(3000)  # 3-second delay before retracting actuator 2 and 3

                    # Timer for second action: retract_button_2.click() (Turn off the pump controller)
                    self.retract_timer = QTimer(self)
                    self.retract_timer.setSingleShot(True)
                    self.retract_timer.timeout.connect(self.stop_button_2.click)
                    self.retract_timer.start(6000)  # 6-second delay

                    # Timer for third action: send_command('R') to extend actuators 2 and 3
                    self.command_timer = QTimer(self)
                    self.command_timer.setSingleShot(True)
                    self.command_timer.timeout.connect(lambda: self.arduino.send_command('R'))
                    self.command_timer.start(9000)  # 9-second delay

                    # Timer for fourth action: Turn off the controller
                    self.pumpOn_timer = QTimer(self)
                    self.pumpOn_timer.setSingleShot(True)
                    self.pumpOn_timer.timeout.connect(self.retract_button_2.click)
                    self.pumpOn_timer.start(12000)  # 12-second delay

                    # Timer for retracting actuator 2 and 3 again
                    self.retract_time_2 = QTimer(self)
                    self.retract_time_2.setSingleShot(True)
                    self.retract_time_2.timeout.connect(lambda: self.arduino.send_command('K'))
                    self.retract_time_2.start(16000)  # 16-second delay

                    self.calib_delay_timer = QTimer(self)
                    self.calib_delay_timer.setSingleShot(True)
                    self.calib_delay_timer.timeout.connect(self.afterDelayToCalib)
                    self.calib_delay_timer.start(21000)  # 5-second delay

                    self.webcam_focus_delay = QTimer(self)
                    self.webcam_focus_delay.setSingleShot(True)
                    self.webcam_focus_delay.timeout.connect(lambda: playsound('Sound/waitToFocus.mp3'))
                    self.webcam_focus_delay.start(41000)  # 20-second delay, wait for accessing calibration mode.

                    self.preopen_air_delay = QTimer(self)
                    self.preopen_air_delay.setSingleShot(True)
                    self.preopen_air_delay.timeout.connect(lambda: playsound('Sound/openAir.mp3'))
                    self.preopen_air_delay.start(46000)  # 5-second delay, wait for webcam.

                    self.opening_air_delay = QTimer(self)
                    self.opening_air_delay.setSingleShot(True)
                    self.opening_air_delay.timeout.connect(self.stop_button_4.click)
                    self.opening_air_delay.start(50000)  # 4-second delay, wait for opening air.

                    self.while_opening_air_delay = QTimer(self)
                    self.while_opening_air_delay.setSingleShot(True)
                    self.while_opening_air_delay.timeout.connect(lambda: playsound('Sound/waitForPressure.mp3'))
                    self.while_opening_air_delay.start(60000)  # 10-second delay, wait for pressue balancing.

                    self.closing_air_delay = QTimer(self)
                    self.closing_air_delay.setSingleShot(True)
                    self.closing_air_delay.timeout.connect(lambda: playsound('Sound/closeAir.mp3'))
                    self.closing_air_delay.start(65000)  # 10-second delay, wait for closing air.

                    self.after_closing_air_delay = QTimer(self)
                    self.after_closing_air_delay.setSingleShot(True)
                    self.after_closing_air_delay.timeout.connect(self.retract_button_4.click)
                    self.after_closing_air_delay.start(69000)  # 4-second delay, wait for closing air sound then close air. 

                    self.preopening_middle_valve_delay = QTimer(self)
                    self.preopening_middle_valve_delay.setSingleShot(True)
                    self.preopening_middle_valve_delay.timeout.connect(lambda: playsound('Sound/middleVavleOpen.mp3'))
                    self.preopening_middle_valve_delay.start(71000)  # 4-second delay, wait for closing air. 

                    self.opening_middle_valve_delay = QTimer(self)
                    self.opening_middle_valve_delay.setSingleShot(True)
                    self.opening_middle_valve_delay.timeout.connect(lambda: self.arduino.send_command('F'))
                    self.opening_middle_valve_delay.start(73000)  # 2-second delay, wait for openning mid air to reduce pressure to 0.

                    self.post_opening_middle_valve_delay = QTimer(self)
                    self.post_opening_middle_valve_delay.setSingleShot(True)
                    self.post_opening_middle_valve_delay.timeout.connect(lambda: self.arduino.send_command('J'))
                    self.post_opening_middle_valve_delay.start(77000)  # 4-second delay, wait for openning mid air to reduce pressure to 0 and then close air.


                elif extracted_text.strip() == "UNLOCKED":
                    self.status_label.setText('UNLOCKED MODE')
                    playsound('Sound/UnlockedMode.mp3')
                    # Implement further logic for unlocked mode
                    self.arduino.send_command('K')  # Retract actuators 2 and 3
                # Introduce a 5-second delay before calling afterDelayToCalib
                    self.calib_delay_timer = QTimer(self)
                    self.calib_delay_timer.setSingleShot(True)
                    self.calib_delay_timer.timeout.connect(self.afterDelayToCalib)
                    self.calib_delay_timer.start(5000)  # 5-second delay

    def afterDelayToCalib(self):
        # Extend actuator 2 and 4
        self.arduino.send_command('D')

        # Timer for playing calibration sound
        self.delay_timer_arduino_to_calib = QTimer(self)
        self.delay_timer_arduino_to_calib.setSingleShot(True)
        self.delay_timer_arduino_to_calib.timeout.connect(lambda: playsound('Sound/calibration_mode.mp3'))
        self.delay_timer_arduino_to_calib.start(16000)  # 16-second delay



    def pumpON(self):
        self.arduino.send_command('B')
        self.status_label.setText('Status: PUMP ON')

    def pumpOFF(self):
        self.arduino.send_command('C')
        self.status_label.setText('Status: PUMP OFF')

    def pressUpArrowandResetButton(self):
        self.arduino.send_command('D')
        self.status_label.setText('Status: Pressing the up arrow and Reset')

    def retract_actuator_3(self):
        self.arduino.send_command('J')
        self.status_label.setText('Status: Retracting Actuator 3')

    def stop_actuator_3(self):
        self.arduino.send_command('F')
        self.status_label.setText('Status: Stopping Actuator 3')

    def extend_actuator_4(self):
        self.arduino.send_command('G')
        self.status_label.setText('Status: Extending Actuator 4')

    def closeAir(self):
        self.arduino.send_command('H')
        self.status_label.setText('Status: closeAir')

    def openAir(self):
        self.arduino.send_command('I')
        self.status_label.setText('Status: openAir')
    
    def retract_acutator_23(self):
        self.arduino.send_command('K')
        self.status_label.setText('Status: Retracting actuator 2 and 3')

    def display_captured_image_msg(self):
        self.status_label.setText('Status: Image captured!')
        self.status_label.setAlignment(Qt.AlignCenter)  # Center-align the text
        self.status_label.setStyleSheet("""
            QLabel {
                color: red;
                border-style: sutset;
                font: bold 25px;                   /* Set the font size */
                border: 3px solid red;             /* Create a red border */
                padding: 10px;                     /* Add padding inside the border */
                border-radius: 5px;                /* Optional: Add rounded corners */
                background-color: white;           /* Optional: Set background color */
            }
        """)
        

    def closeEvent(self, event):
        self.arduino.close()
        self.cap.release()
        event.accept()
