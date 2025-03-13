# config.py
# Global configuration settings for the application

# OCR capture rectangle dimensions
OCR_RECT_X = 120
OCR_RECT_Y = 245
OCR_RECT_WIDTH = 400
OCR_RECT_HEIGHT = 120

# Camera settings
CAMERA_INDEX = 2  # Default camera index
CAPTURE_PATH = "/home/dinh/Documents/PlatformIO/Projects/kelco_test_001/SnapShotImages"

# Serial communication settings
SERIAL_PORT = '/dev/ttyACM1'
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT = 1

# UI update frequency (in milliseconds)
WEBCAM_UPDATE_INTERVAL = 30