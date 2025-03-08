# Implementation Steps for Threaded Webcam Processing

# Step 1: Create a new file named webcam_thread.py with this content:

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2
import time
import threading
import numpy as np

class WebcamThread(QThread):
    update_frame_signal = pyqtSignal(QImage)
    
    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.cap = None
        self._latest_frame = None
        self._frame_lock = threading.Lock()
        
    def start_capture(self, camera_index=None):
        if camera_index is not None:
            self.camera_index = camera_index
            
        # Open camera
        self.cap = cv2.VideoCapture(self.camera_index)
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Use minimal buffer
        self.cap.set(cv2.CAP_PROP_FPS, 30)  # Request 30 FPS if supported
        
        if not self.cap.isOpened():
            print(f"Error: Could not open camera at index {self.camera_index}")
            return False
            
        # Start the thread
        self.running = True
        if not self.isRunning():
            self.start()
        return True
            
    def stop_capture(self):
        self.running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None
        # Thread will exit in its run loop
        self.wait()  # Wait for thread to finish
    
    def get_latest_frame(self):
        """Return the most recent frame as an OpenCV BGR image"""
        with self._frame_lock:
            if self._latest_frame is not None:
                return self._latest_frame.copy()
            return None
        
    def run(self):
        while self.running:
            if self.cap and self.cap.isOpened():
                # Flush buffer to get the latest frame
                for _ in range(2):
                    self.cap.grab()
                    
                # Get frame
                ret, frame = self.cap.retrieve()
                if ret:
                    # Store the latest BGR frame for direct access
                    with self._frame_lock:
                        self._latest_frame = frame.copy()
                    
                    # Convert to RGB for Qt
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Convert to QImage
                    h, w, ch = rgb_frame.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    
                    # Emit signal with the image
                    self.update_frame_signal.emit(qt_image)
