from PyQt5.QtWidgets import QApplication
from gui import ActuatorControl
import sys

def main():
    app = QApplication(sys.argv)
    window = ActuatorControl()
    window.show()
    sys.exit(app.exec_()) 
if __name__ == '__main__':
    main()
