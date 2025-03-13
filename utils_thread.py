from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
import serial
import queue
import time

class SerialCommunicator(QThread):
    # Signals
    response_signal = pyqtSignal(str)  # Emitted when a response is received
    error_signal = pyqtSignal(str)     # Emitted when an error occurs
    connected_signal = pyqtSignal(bool)  # Emitted when connection status changes
    
    def __init__(self, port, baudrate=9600, timeout=1):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        
        # Thread control
        self.running = False
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        
        # Command queue with priority
        self.command_queue = queue.PriorityQueue()
        
        # Response buffer
        self.last_response = None
        
    def connect_serial(self):
        """Establish serial connection"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            # Ensure connection is ready
            if not self.serial_conn.is_open:
                self.serial_conn.open()
            print(f"Connected to {self.port} at {self.baudrate} baud")
            self.connected_signal.emit(True)
            return True
        except Exception as e:
            error_msg = f"Failed to connect to serial port: {str(e)}"
            print(error_msg)
            self.error_signal.emit(error_msg)
            self.serial_conn = None
            self.connected_signal.emit(False)
            return False
            
    def run(self):
        """Main thread loop"""
        self.running = True
        
        # Try to connect initially
        if not self.connect_serial():
            # If initial connection fails, try again in the loop
            pass
            
        # Main communication loop
        while self.running:
            # Check if we need to reconnect
            if self.serial_conn is None or not self.serial_conn.is_open:
                self.connect_serial()
                time.sleep(1)  # Wait before trying again
                continue
                
            try:
                # Process any commands in the queue
                if not self.command_queue.empty():
                    # Get the next command (priority, command string)
                    priority, command = self.command_queue.get(block=False)
                    
                    # Send the command
                    self.serial_conn.write(command.encode())
                    self.serial_conn.flush()  # Force write
                    print(f"Sent command with priority {priority}: {command.strip()}")
                    
                    self.command_queue.task_done()
                
                # Check for any responses
                if self.serial_conn.in_waiting > 0:
                    response = self.serial_conn.readline().decode().strip()
                    if response:
                        print(f"Received: {response}")
                        self.last_response = response
                        self.response_signal.emit(response)
                
                # Small sleep to prevent high CPU usage
                time.sleep(0.01)  # 10ms
                
                # Wait for condition if no activity
                self.mutex.lock()
                if self.command_queue.empty() and self.serial_conn.in_waiting == 0:
                    # Wait for a signal to wake up (new command or stop request)
                    self.condition.wait(self.mutex, 100)  # 100ms timeout
                self.mutex.unlock()
                
            except Exception as e:
                error_msg = f"Serial communication error: {str(e)}"
                print(error_msg)
                self.error_signal.emit(error_msg)
                
                # Close and reset connection on error
                try:
                    if self.serial_conn and self.serial_conn.is_open:
                        self.serial_conn.close()
                except:
                    pass
                self.serial_conn = None
                time.sleep(1)  # Wait before trying to reconnect
        
        # Clean up when thread exits
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            
    def send_command(self, command, priority=5):
        """
        Send a command to the Arduino with priority
        Priority levels:
        1 = Emergency/Stop (highest)
        2 = Critical operations
        3 = Important operations
        4 = Normal operations
        5 = Low priority (default)
        """
        # If it's a stop command, use highest priority
        if command.strip().upper() == "STOP":
            priority = 1
            
        # Ensure command ends with carriage return AND newline
        if not command.endswith('\r\n'):
            command = command.strip() + '\r\n'
            
        # Add to queue with priority
        self.mutex.lock()
        self.command_queue.put((priority, command))
        self.condition.wakeAll()  # Wake up the thread
        self.mutex.unlock()
        
    def read_last_response(self):
        """Return the last received response"""
        return self.last_response
        
    def clear_queue(self):
        """Clear all pending commands except emergency ones"""
        # Create a new queue with only priority 1 commands
        new_queue = queue.PriorityQueue()
        
        self.mutex.lock()
        while not self.command_queue.empty():
            try:
                item = self.command_queue.get(block=False)
                # Only keep emergency commands
                if item[0] == 1:
                    new_queue.put(item)
            except queue.Empty:
                break
        # Replace the queue
        self.command_queue = new_queue
        self.mutex.unlock()
        
    def emergency_stop(self):
        """Send emergency stop command and clear queue"""
        # Clear all pending commands first
        self.clear_queue()
        
        # Send STOP command with highest priority
        self.send_command("STOP", priority=1)
        
    def stop(self):
        """Stop the serial communication thread"""
        self.mutex.lock()
        self.running = False
        self.condition.wakeAll()  # Wake up the thread to check running flag
        self.mutex.unlock()
        
        # Wait for the thread to finish
        if not self.wait(1000):  # Wait up to 1 second
            print("Warning: SerialCommunicator thread did not exit cleanly")