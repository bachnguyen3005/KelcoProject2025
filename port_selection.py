from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
import serial
import serial.tools.list_ports

class PortSelectionDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(PortSelectionDialog, self).__init__(parent)
        self.setWindowTitle("Device Connection Setup")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Set a clean, modern style
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #2c3e50;
                font-size: 16px;
                padding: 5px;
            }
            QComboBox {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 5px;
                min-height: 30px;
                font-size: 14px;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 16px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QGroupBox {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title label
        title_label = QtWidgets.QLabel("Device Connection Setup")
        title_font = QtGui.QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Webcam group
        webcam_group = QtWidgets.QGroupBox("Webcam Selection")
        webcam_layout = QtWidgets.QVBoxLayout(webcam_group)
        
        # Webcam selection
        self.webcam_combo = QtWidgets.QComboBox()
        self.webcam_combo.setMinimumHeight(40)
        self.refresh_webcam_button = QtWidgets.QPushButton("Refresh")
        
        webcam_combo_layout = QtWidgets.QHBoxLayout()
        webcam_combo_layout.addWidget(QtWidgets.QLabel("Select Webcam:"))
        webcam_combo_layout.addWidget(self.webcam_combo)
        webcam_combo_layout.addWidget(self.refresh_webcam_button)
        
        # Webcam preview
        self.preview_button = QtWidgets.QPushButton("Preview")
        preview_layout = QtWidgets.QHBoxLayout()
        preview_layout.addStretch()
        preview_layout.addWidget(self.preview_button)
        
        webcam_layout.addLayout(webcam_combo_layout)
        webcam_layout.addLayout(preview_layout)
        
        # Arduino group
        arduino_group = QtWidgets.QGroupBox("Arduino Serial Port")
        arduino_layout = QtWidgets.QVBoxLayout(arduino_group)
        
        # Arduino port selection
        self.arduino_combo = QtWidgets.QComboBox()
        self.arduino_combo.setMinimumHeight(40)
        self.refresh_arduino_button = QtWidgets.QPushButton("Refresh")
        
        arduino_combo_layout = QtWidgets.QHBoxLayout()
        arduino_combo_layout.addWidget(QtWidgets.QLabel("Select Serial Port:"))
        arduino_combo_layout.addWidget(self.arduino_combo)
        arduino_combo_layout.addWidget(self.refresh_arduino_button)
        
        # Baudrate selection
        self.baudrate_combo = QtWidgets.QComboBox()
        self.baudrate_combo.setMinimumHeight(40)
        self.baudrate_combo.addItems(["9600"])
        self.baudrate_combo.setCurrentText("9600")  # Default baudrate
        
        baudrate_layout = QtWidgets.QHBoxLayout()
        baudrate_layout.addWidget(QtWidgets.QLabel("Baudrate:"))
        baudrate_layout.addWidget(self.baudrate_combo)
        
        arduino_layout.addLayout(arduino_combo_layout)
        arduino_layout.addLayout(baudrate_layout)
        
        # Add groups to main layout
        layout.addWidget(webcam_group)
        layout.addWidget(arduino_group)
        
        # Button layout
        button_layout = QtWidgets.QHBoxLayout()
        self.ok_button = QtWidgets.QPushButton("OK")
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setStyleSheet("background-color: #e74c3c;")
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.refresh_webcam_button.clicked.connect(self.populate_webcam_list)
        self.refresh_arduino_button.clicked.connect(self.populate_serial_ports)
        self.preview_button.clicked.connect(self.preview_webcam)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Initialize
        self.populate_webcam_list()
        self.populate_serial_ports()
        
        # Store selected values
        self.selected_webcam_index = -1
        self.selected_arduino_port = ""
        self.selected_baudrate = 9600
    
    def populate_webcam_list(self):
        """Populate the webcam combo box with available webcams"""
        self.webcam_combo.clear()
        
        # Try to detect cameras
        webcams = []
        for i in range(10):  # Check first 10 indexes
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                webcams.append(f"Camera {i}")
                cap.release()
        
        if webcams:
            self.webcam_combo.addItems(webcams)
        else:
            self.webcam_combo.addItem("No webcams found")
    
    def populate_serial_ports(self):
        """Populate the Arduino serial port combo box"""
        self.arduino_combo.clear()
        
        try:
            # Get list of available serial ports
            ports = list(serial.tools.list_ports.comports())
            
            if ports:
                for port in ports:
                    self.arduino_combo.addItem(f"{port.device} - {port.description}")
            else:
                self.arduino_combo.addItem("No serial ports found")
        except Exception as e:
            self.arduino_combo.addItem(f"Error: {str(e)}")
    
    def preview_webcam(self):
        """Show a preview of the selected webcam"""
        if self.webcam_combo.currentText().startswith("No webcams"):
            QtWidgets.QMessageBox.warning(self, "Warning", "No webcams available")
            return
        
        # Extract the webcam index from the combo box
        try:
            camera_index = int(self.webcam_combo.currentText().split(" ")[1])
            
            # Open the webcam
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                QtWidgets.QMessageBox.warning(self, "Warning", "Failed to open webcam")
                return
            
            # Create a preview dialog
            preview_dialog = QtWidgets.QDialog(self)
            preview_dialog.setWindowTitle("Webcam Preview")
            preview_dialog.setMinimumSize(640, 480)
            
            # Create layout
            layout = QtWidgets.QVBoxLayout(preview_dialog)
            
            # Create label for the preview
            preview_label = QtWidgets.QLabel()
            layout.addWidget(preview_label)
            
            # Button to close the preview
            close_button = QtWidgets.QPushButton("Close Preview")
            close_button.clicked.connect(preview_dialog.accept)
            layout.addWidget(close_button)
            
            # Timer for updating the preview
            timer = QtCore.QTimer(preview_dialog)
            
            # Function to update the preview
            def update_preview():
                ret, frame = cap.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = frame_rgb.shape
                    bytes_per_line = ch * w
                    qt_image = QtGui.QImage(frame_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                    preview_label.setPixmap(QtGui.QPixmap.fromImage(qt_image))
            
            # Connect timer to update function
            timer.timeout.connect(update_preview)
            timer.start(30)  # Update every 30ms
            
            # Connect dialog close event to stop the timer and release the webcam
            def on_close():
                timer.stop()
                cap.release()
            
            preview_dialog.finished.connect(on_close)
            
            # Show the dialog
            preview_dialog.exec_()
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to preview webcam: {str(e)}")
    
    def get_selected_values(self):
        """Get the selected webcam, Arduino port, and baudrate"""
        try:
            # Get webcam index
            if self.webcam_combo.currentText().startswith("Camera "):
                self.selected_webcam_index = int(self.webcam_combo.currentText().split(" ")[1])
            else:
                self.selected_webcam_index = -1
            
            # Get Arduino port
            if not self.arduino_combo.currentText().startswith("No serial"):
                self.selected_arduino_port = self.arduino_combo.currentText().split(" - ")[0]
            else:
                self.selected_arduino_port = ""
            
            # Get baudrate
            self.selected_baudrate = int(self.baudrate_combo.currentText())
            
            return (self.selected_webcam_index, self.selected_arduino_port, self.selected_baudrate)
        except Exception as e:
            print(f"Error getting selected values: {str(e)}")
            return (-1, "", 9600)