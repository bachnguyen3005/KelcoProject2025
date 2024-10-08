### How to auto-start the GUI on Pi
```
crontab -e
Then uncommand the @reboot ....

Ctrl+X
Y
Enter

```

### Note

```
The GUI can be launch with full-screen or normal mode.

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.showMaximized() # Change this to showFullScreen()
    sys.exit(app.exec_())
```
