import cv2
import numpy as np

class LEDDetector:
    def __init__(self):
        # Define color ranges in HSV
        self.color_ranges = {
            'green': (np.array([40, 70, 70]), np.array([90, 255, 255])),
            'red1': (np.array([0, 100, 100]), np.array([10, 255, 255])),  # Red wraps around in HSV
            'red2': (np.array([160, 100, 100]), np.array([180, 255, 255])),  # Second part of red range
            'yellow': (np.array([20, 100, 100]), np.array([40, 255, 255])),
            'blue': (np.array([100, 100, 100]), np.array([140, 255, 255]))
        }
    
    def detect_leds(self, frame, box_coordinates):
        """
        Detect LEDs in specified box coordinates and determine if they are lit up and their color.
        
        Args:
            frame: The image frame to analyze
            box_coordinates (list): List of boxes defined as [x, y, width, height]
        
        Returns:
            list: Status of each box containing LED information
            image: Annotated image showing the detection results
        """
        # Make a copy of the frame for display
        display_img = frame.copy()
        
        # Convert to HSV for better color detection
        img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Results list
        results = []
        
        # Process each box
        for i, box in enumerate(box_coordinates):
            x, y, w, h = box
            
            # Ensure coordinates are within image bounds
            x = max(0, min(x, frame.shape[1]-1))
            y = max(0, min(y, frame.shape[0]-1))
            w = min(w, frame.shape[1] - x)
            h = min(h, frame.shape[0] - y)
            
            # Extract the region of interest (ROI)
            roi = img_hsv[y:y+h, x:x+w]
            
            if roi.size == 0:  # Check if ROI is valid
                results.append({
                    'box_id': i+1,
                    'lit': False,
                    'color': 'none',
                    'message': 'Invalid box coordinates'
                })
                continue
            
            # Draw the box on the display image
            cv2.rectangle(display_img, (x, y), (x+w, y+h), (255, 255, 255), 2)
            
            # Check if LED is lit in the box
            brightness = np.mean(roi[:,:,2])  # Value channel in HSV represents brightness
            is_lit = brightness > 100  # Threshold can be adjusted
            
            # Determine the color if lit
            color_found = 'unknown'
            max_color_pixels = 0
            
            if is_lit:
                red_pixels = 0
                
                for color_name, (lower, upper) in self.color_ranges.items():
                    mask = cv2.inRange(roi, lower, upper)
                    pixel_count = cv2.countNonZero(mask)
                    
                    if color_name == 'red1' or color_name == 'red2':
                        red_pixels += pixel_count
                    elif pixel_count > max_color_pixels:
                        max_color_pixels = pixel_count
                        color_found = color_name
                
                # Check if red is the dominant color
                if red_pixels > max_color_pixels:
                    max_color_pixels = red_pixels
                    color_found = 'red'
            
            # Generate text to display on the image
            status_text = f"LED {i+1}: {'ON' if is_lit else 'OFF'}"
            color_text = f"Color: {color_found}" if is_lit else ""
            
            # Add text to the display image
            cv2.putText(display_img, status_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            if is_lit:
                cv2.putText(display_img, color_text, (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Save the result
            results.append({
                'box_id': i+1,
                'lit': is_lit,
                'color': color_found if is_lit else 'none',
                'brightness': brightness,
                'position': f"x={x}, y={y}, width={w}, height={h}"
            })
        
        return results, display_img
    
    def check_green_leds(self, results):
        """
        Check if there are exactly two green LEDs lit up.
        
        Args:
            results (list): List of LED detection results
        
        Returns:
            bool: True if exactly 2 green LEDs are lit, False otherwise
            str: Detailed result message
        """
        green_leds_count = sum(1 for r in results if r['lit'] and r['color'] == 'green')
        
        if green_leds_count == 2:
            message = f"SUCCESSFUL: Exactly 2 green LEDs are lit up."
            return True, message
        else:
            message = f"FAILED: Expected 2 green LEDs, but detected {green_leds_count}."
            return False, message

    def detect_blinking_led(self, webcam_thread, led_box_coordinates, position_index=1, num_frames=10, interval_ms=200):
        """
        Detect if an LED is blinking by capturing multiple frames and analyzing them.
        
        Args:
            webcam_thread: WebcamThread object that provides frames
            led_box_coordinates: List of boxes defined as [x, y, width, height]
            position_index: Index of the LED position to check (0-based)
            num_frames: Number of frames to capture for blink detection
            interval_ms: Time interval between frame captures in milliseconds
            
        Returns:
            dict: Detection results with the following keys:
                - is_blinking: True if LED is detected as blinking
                - frames_on: Number of frames where LED was detected as ON
                - frames_off: Number of frames where LED was detected as OFF
                - message: Detailed result message
                - states: List of LED states across frames (True for ON, False for OFF)
        """
        import time
        from datetime import datetime
        import cv2
        import os
        
        # Input validation
        if position_index >= len(led_box_coordinates):
            return {
                'is_blinking': False,
                'frames_on': 0,
                'frames_off': 0,
                'message': f"Error: Position index {position_index} is out of range",
                'states': []
            }
        
        # Initialize result tracking
        states = []
        frames = []
        timestamps = []
        
        print(f"Starting blink detection for LED at position {position_index+1}...")
        print(f"Capturing {num_frames} frames with {interval_ms}ms interval")
        
        # Create a directory for saving frames if it doesn't exist
        save_dir = "/home/dinh/Documents/PlatformIO/Projects/kelco_test_001/SnapShotImages/blink_detection"
        os.makedirs(save_dir, exist_ok=True)
        
        # Get timestamp for this session
        session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Capture multiple frames with time intervals
        for i in range(num_frames):
            # Get current timestamp
            current_time = datetime.now()
            timestamps.append(current_time)
            
            # Get the latest frame from the webcam
            frame = webcam_thread.get_latest_frame()
            
            if frame is None:
                print(f"Error capturing frame {i+1}")
                continue
            
            # Save the frame
            frame_filename = f"{save_dir}/blink_frame_{session_timestamp}_{i+1}.jpg"
            cv2.imwrite(frame_filename, frame)
            
            # Detect LEDs in the frame
            results, annotated_frame = self.detect_leds(frame, led_box_coordinates)
            
            # Save the annotated frame
            annotated_filename = f"{save_dir}/blink_annotated_{session_timestamp}_{i+1}.jpg"
            cv2.imwrite(annotated_filename, cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR))
            
            # Store the frame for later use
            frames.append(frame)
            
            # Check if the LED at the specified position is lit
            if position_index < len(results):
                led_state = results[position_index]['lit']
                led_color = results[position_index]['color'] if led_state else 'none'
                states.append(led_state)
                print(f"Frame {i+1}: LED {position_index+1} is {'ON' if led_state else 'OFF'} " + 
                    (f"(Color: {led_color})" if led_state else ""))
            else:
                print(f"Error: Position {position_index+1} not found in results")
                states.append(False)
            
            # Wait for the specified interval
            if i < num_frames - 1:  # Don't wait after the last frame
                time.sleep(interval_ms / 1000.0)
        
        # Analyze the results
        frames_on = sum(states)
        frames_off = len(states) - frames_on
        
        # Check if we detected both ON and OFF states (indicating blinking)
        is_blinking = frames_on > 0 and frames_off > 0
        
        # Create result message
        if len(states) == 0:
            message = "Error: No frames were successfully analyzed"
        elif is_blinking:
            message = f"LED at position {position_index+1} is BLINKING (ON: {frames_on} frames, OFF: {frames_off} frames)"
        elif frames_on == len(states):
            message = f"LED at position {position_index+1} is CONSTANTLY ON (all {frames_on} frames)"
        else:
            message = f"LED at position {position_index+1} is CONSTANTLY OFF (all {frames_off} frames)"
        
        # Save a summary file with timestamps and states
        summary_filename = f"{save_dir}/blink_summary_{session_timestamp}.txt"
        with open(summary_filename, 'w') as f:
            f.write(f"Blink detection for LED at position {position_index+1}\n")
            f.write(f"Session: {session_timestamp}\n")
            f.write(f"Frames captured: {len(states)}\n")
            f.write(f"Results: {message}\n\n")
            f.write("Frame-by-frame results:\n")
            for i, (timestamp, state) in enumerate(zip(timestamps, states)):
                f.write(f"Frame {i+1} [{timestamp.strftime('%H:%M:%S.%f')[:-3]}]: {'ON' if state else 'OFF'}\n")
        
        print(message)
        
        return {
            'is_blinking': is_blinking,
            'frames_on': frames_on,
            'frames_off': frames_off,
            'message': message,
            'states': states
        }