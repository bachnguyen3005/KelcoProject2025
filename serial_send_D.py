import serial
import time

# Replace 'COM3' with the appropriate port (e.g., /dev/ttyUSB0 for Linux/Raspberry Pi)
serial_port = '/dev/ttyUSB0'  # or '/dev/ttyUSB0' on Raspberry Pi/Linux
baud_rate = 115200  # Make sure this matches your device's baud rate

try:
    # Open the serial port
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Connected to {serial_port}")

    # Allow some time for the connection to establish
    time.sleep(2)

    # Send the letter 'D'
    ser.write(b'D')
    print("Sent: 'D'")

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")

finally:
    # Close the serial port
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed.")
