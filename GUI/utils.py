import serial

class SerialCommunicator:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)

    def send_command(self, command):
        self.ser.write(command.encode())
        
    def read_command(self, max_wait_time=6):
        import time
        start_time = time.time()
        data = None
        while True:
            if self.ser.in_waiting > 0:
                data = self.ser.readline().decode('utf-8').rstrip()
                if data:
                    return data
            if time.time() - start_time > max_wait_time:
                print("Timed out waiting for data")
                break
        return data


    def close(self):
        if self.ser.is_open:
            self.ser.close()
