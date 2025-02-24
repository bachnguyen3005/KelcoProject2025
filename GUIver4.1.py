from PyQt5 import QtWidgets, uic
import sys

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Load the UI file directly
        uic.loadUi('GUIver4.1.ui', self)
        
        # Now you can access UI elements directly
        self.populate_model_list()
        
        # Connect signals
        self.startButton.clicked.connect(self.on_start_clicked)
        
    def populate_model_list(self):
        # Add items to the combo box
        models = ["Model A", "Model B", "Model C", "Model D"]
        self.modelList.addItems(models)
        
    def on_start_clicked(self):
        # Handle the start button click
        selected_model = self.modelList.currentText()
        self.lowVoltageTestResult.setText("OK")
        self.highVoltageTestResult.setText("ERROR")
        self.kpaNumber.setText("495")
        print(f"Test started for model: {selected_model}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())