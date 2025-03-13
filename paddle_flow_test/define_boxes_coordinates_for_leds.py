import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button
import os
import json
import time
from datetime import datetime

class WebcamLEDDetector:
    def __init__(self, camera_id=0, config_file="led_boxes.json"):
        self.camera_id = camera_id
        self.config_file = config_file
        self.cap = None
        self.boxes = []
        self.results_history = []
        self.running = False
        self.frame_count = 0
        self.start_time = None
        self.last_save_time = None
        self.save_interval = 5  # Save results every 5 seconds
        
        # Initialize color ranges for LED detection
        self.color_ranges = {
            'green': (np.array([40, 70, 70]), np.array([90, 255, 255])),
            'red1': (np.array([0, 100, 100]), np.array([10, 255, 255])),  # Red wraps around in HSV
            'red2': (np.array([160, 100, 100]), np.array([180, 255, 255])),  # Second part of red range
            'yellow': (np.array([20, 100, 100]), np.array([40, 255, 255])),
            'blue': (np.array([100, 100, 100]), np.array([140, 255, 255]))
        }
        
        # Create results directory if it doesn't exist
        self.results_dir = "led_webcam_results"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def load_boxes(self):
        """Load predefined LED boxes from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.boxes = json.load(f)
            print(f"Loaded {len(self.boxes)} boxes from {self.config_file}")
            return True
        else:
            print(f"No box configuration found at {self.config_file}")
            return False
    
    def setup_webcam(self):
        """Initialize the webcam capture"""
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_id}")
            return False
        
        # Get webcam properties
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        
        print(f"Webcam initialized: {frame_width}x{frame_height} at {fps} fps")
        return True
    
    def define_boxes_interactively(self):
        """Allow user to define LED boxes interactively on a webcam frame"""
        if not self.setup_webcam():
            return False
        
        # Capture a single frame for box definition
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame from webcam")
            self.cap.release()
            return False
        
        # Convert to RGB for matplotlib
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Close the webcam temporarily
        self.cap.release()
        
        # Create a temporary file to store the frame
        temp_frame_path = os.path.join(self.results_dir, "temp_webcam_frame.jpg")
        cv2.imwrite(temp_frame_path, frame)
        
        # Use the existing LEDBoxSelector to define boxes
        selector = LEDBoxSelector(temp_frame_path)
        
        # Boxes will be saved to the config file by the selector
        print("Please define LED boxes on the captured frame")
        
        # Reopen webcam when done
        self.setup_webcam()
        return True
    
    def detect_leds_in_frame(self, frame):
        """
        Detect LEDs in the current frame using the predefined boxes.
        
        Args:
            frame: Current webcam frame
        
        Returns:
            results: List of dictionaries with LED detection results
            display_frame: Frame with detection results visualized
        """
        if not self.boxes:
            return [], frame
        
        # Convert to RGB and HSV
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create a copy for visualization
        display_frame = frame.copy()
        
        # Results list
        results = []
        
        # Process each box
        for i, (x, y, w, h) in enumerate(self.boxes):
            # Ensure coordinates are within frame bounds
            frame_height, frame_width = frame.shape[:2]
            x = max(0, min(x, frame_width-1))
            y = max(0, min(y, frame_height-1))
            w = min(w, frame_width - x)
            h = min(h, frame_height - y)
            
            # Extract the region of interest (ROI)
            roi = frame_hsv[y:y+h, x:x+w]
            
            if roi.size == 0:  # Check if ROI is valid
                results.append({
                    'box_id': i+1,
                    'lit': False,
                    'color': 'none',
                    'message': 'Invalid box coordinates'
                })
                continue
            
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
                        if red_pixels > max_color_pixels:
                            max_color_pixels = red_pixels
                            color_found = 'red'
                    else:
                        if pixel_count > max_color_pixels:
                            max_color_pixels = pixel_count
                            color_found = color_name
            
            # Draw the box with color based on state
            box_color = (0, 255, 0) if is_lit else (0, 0, 255)  # Green if ON, Red if OFF
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), box_color, 2)
            
            # Generate text to display on the image
            status_text = f"LED {i+1}: {'ON' if is_lit else 'OFF'}"
            color_text = f"Color: {color_found}" if is_lit else ""
            
            # Add text to the image
            cv2.putText(display_frame, status_text, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            if is_lit:
                cv2.putText(display_frame, color_text, (x, y-30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Save the result
            results.append({
                'box_id': i+1,
                'lit': is_lit,
                'color': color_found if is_lit else 'none',
                'brightness': brightness,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            })
        
        return results, display_frame
    
    def save_results(self, results, frame):
        """Save detection results and the current frame"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save results to JSON
        results_file = os.path.join(self.results_dir, f"led_results_{timestamp}.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=4)
        
        # Save frame with detection visualization
        frame_file = os.path.join(self.results_dir, f"led_frame_{timestamp}.jpg")
        cv2.imwrite(frame_file, frame)
        
        print(f"Saved results to {results_file} and frame to {frame_file}")
    
    def display_status(self, frame, results):
        """Add status information to the display frame"""
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Add FPS
        if self.start_time is not None and self.frame_count > 0:
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Add LED summary at the bottom
        y_pos = frame.shape[0] - 20
        led_statuses = []
        for r in results:
            if r['lit']:
                led_statuses.append(f"LED {r['box_id']}: {r['color'].upper()}")
            else:
                led_statuses.append(f"LED {r['box_id']}: OFF")
        
        status_text = " | ".join(led_statuses)
        cv2.putText(frame, status_text, (10, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame
    
    def run(self):
        """Run the webcam LED detector in a continuous loop"""
        if not self.boxes:
            if not self.load_boxes():
                print("No boxes defined. Let's define them now.")
                self.define_boxes_interactively()
                if not self.boxes:
                    print("No boxes defined. Exiting.")
                    return
        
        if not self.setup_webcam():
            return
        
        self.running = True
        self.frame_count = 0
        self.start_time = time.time()
        self.last_save_time = time.time()
        
        print("Starting webcam LED detection. Press 'q' to quit, 's' to save current results.")
        
        try:
            while self.running:
                # Capture frame
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to grab frame from webcam")
                    break
                
                # Detect LEDs
                results, display_frame = self.detect_leds_in_frame(frame)
                
                # Add current results to history
                self.results_history.append(results)
                if len(self.results_history) > 100:  # Keep last 100 frames
                    self.results_history = self.results_history[-100:]
                
                # Add status information
                display_frame = self.display_status(display_frame, results)
                
                # Show the frame
                cv2.imshow('Webcam LED Detection', display_frame)
                
                # Save results periodically
                current_time = time.time()
                if current_time - self.last_save_time >= self.save_interval:
                    self.save_results(results, display_frame)
                    self.last_save_time = current_time
                
                # Check for key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Quitting...")
                    self.running = False
                elif key == ord('s'):
                    print("Saving current results...")
                    self.save_results(results, display_frame)
                
                self.frame_count += 1
                
        except KeyboardInterrupt:
            print("\nStopped by user")
        finally:
            # Clean up
            if self.cap is not None:
                self.cap.release()
            cv2.destroyAllWindows()
            
            # Save final results
            if self.results_history:
                print("Saving final summary...")
                self.save_summary()
    
    def save_summary(self):
        """Save a summary of the detection session"""
        if not self.results_history:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = os.path.join(self.results_dir, f"led_summary_{timestamp}.json")
        
        # Calculate statistics
        duration = time.time() - self.start_time if self.start_time else 0
        fps = self.frame_count / duration if duration > 0 else 0
        
        # Analyze LED states over time
        led_stats = {}
        for box_id in range(1, len(self.boxes) + 1):
            led_stats[f"LED_{box_id}"] = {
                "on_frames": sum(1 for r in self.results_history if any(led['box_id'] == box_id and led['lit'] for led in r)),
                "off_frames": sum(1 for r in self.results_history if any(led['box_id'] == box_id and not led['lit'] for led in r)),
                "colors": {}
            }
            
            # Count color occurrences
            for r in self.results_history:
                for led in r:
                    if led['box_id'] == box_id and led['lit']:
                        color = led['color']
                        if color in led_stats[f"LED_{box_id}"]["colors"]:
                            led_stats[f"LED_{box_id}"]["colors"][color] += 1
                        else:
                            led_stats[f"LED_{box_id}"]["colors"][color] = 1
        
        summary = {
            "session_start": datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S") if self.start_time else None,
            "session_end": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": duration,
            "total_frames": self.frame_count,
            "fps": fps,
            "led_statistics": led_stats
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=4)
        
        print(f"Summary saved to {summary_file}")


class LEDBoxSelector:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise FileNotFoundError(f"Could not load image from {image_path}")
        
        self.image_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.boxes = []
        self.current_box = []
        self.drawing = False
        self.temp_patches = []  # Track temporary patches
        self.box_colors = ['r', 'g', 'b', 'c', 'm', 'y']  # Colors for different boxes
        self.fig, self.ax = plt.subplots(figsize=(12, 10))
        self.setup_figure()
    
    def setup_figure(self):
        """Set up the matplotlib figure and connect event handlers"""
        self.ax.imshow(self.image_rgb)
        self.ax.set_title('Click and drag to define LED boxes (max 3)\nPress Save when done')
        
        # Connect events
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
        # Add buttons
        plt.subplots_adjust(bottom=0.2)
        self.save_button_ax = plt.axes([0.7, 0.05, 0.1, 0.075])
        self.reset_button_ax = plt.axes([0.81, 0.05, 0.1, 0.075])
        
        self.save_button = Button(self.save_button_ax, 'Save')
        self.save_button.on_clicked(self.save_boxes)
        
        self.reset_button = Button(self.reset_button_ax, 'Reset')
        self.reset_button.on_clicked(self.reset_boxes)
        
        plt.show()
    
    def on_press(self, event):
        """Handle mouse button press event"""
        if event.inaxes != self.ax:
            return
        
        if len(self.boxes) >= 3:
            print("Maximum 3 boxes allowed! Use Reset to start over.")
            return
        
        self.drawing = True
        self.current_box = [event.xdata, event.ydata]
    
    def on_motion(self, event):
        """Handle mouse motion event"""
        if not self.drawing or event.inaxes != self.ax:
            return
        
        # Remove any temporary rectangle
        for patch in self.temp_patches:
            patch.remove()
        self.temp_patches = []
        
        x0, y0 = self.current_box
        x1, y1 = event.xdata, event.ydata
        width = x1 - x0
        height = y1 - y0
        
        # Add temporary rectangle
        rect = patches.Rectangle((x0, y0), width, height, linewidth=2, 
                                edgecolor=self.box_colors[len(self.boxes) % len(self.box_colors)], 
                                facecolor='none')
        self.ax.add_patch(rect)
        self.temp_patches.append(rect)
        self.fig.canvas.draw_idle()
    
    def on_release(self, event):
        """Handle mouse button release event"""
        if not self.drawing or event.inaxes != self.ax:
            return
        
        self.drawing = False
        
        # Remove temporary patches
        for patch in self.temp_patches:
            patch.remove()
        self.temp_patches = []
        
        # Get the coordinates
        x0, y0 = self.current_box
        x1, y1 = event.xdata, event.ydata
        
        # Ensure the coordinates are ordered correctly (top-left, width, height)
        x = min(x0, x1)
        y = min(y0, y1)
        w = abs(x1 - x0)
        h = abs(y1 - y0)
        
        # Don't add very small boxes (might be accidental clicks)
        if w < 5 or h < 5:
            print("Box too small, ignoring")
            self.fig.canvas.draw_idle()
            return
        
        # Round to integers for pixel coordinates
        box = (int(x), int(y), int(w), int(h))
        self.boxes.append(box)
        
        # Add permanent rectangle
        rect = patches.Rectangle((x, y), w, h, linewidth=2, 
                                edgecolor=self.box_colors[(len(self.boxes)-1) % len(self.box_colors)], 
                                facecolor='none')
        self.ax.add_patch(rect)
        
        # Add box number
        self.ax.text(x, y-10, f"Box {len(self.boxes)}", color='white', 
                    backgroundcolor=self.box_colors[(len(self.boxes)-1) % len(self.box_colors)],
                    fontsize=12, weight='bold')
        
        print(f"Added Box {len(self.boxes)}: x={box[0]}, y={box[1]}, width={box[2]}, height={box[3]}")
        self.fig.canvas.draw_idle()
    
    def reset_boxes(self, event):
        """Reset all boxes"""
        self.boxes = []
        
        # Properly remove all patches
        for patch in self.ax.patches:
            patch.remove()
            
        # Properly remove all texts
        for text in self.ax.texts:
            text.remove()
            
        self.ax.set_title('Click and drag to define LED boxes (max 3)\nPress Save when done')
        self.fig.canvas.draw_idle()
        print("All boxes reset")
    
    def save_boxes(self, event):
        """Save boxes to file and close the figure"""
        if not self.boxes:
            print("No boxes defined. Please define at least one box before saving.")
            return
        
        # Save boxes to file
        config_file = "led_boxes.json"
        with open(config_file, 'w') as f:
            json.dump(self.boxes, f, indent=4)
        
        print(f"Saved {len(self.boxes)} boxes to {config_file}")
        plt.close(self.fig)


if __name__ == "__main__":
    # Create the webcam LED detector
    detector = WebcamLEDDetector(camera_id=0)  # Use camera ID 0 (default webcam)
    
    # Check if boxes are already defined
    if not detector.load_boxes():
        print("No box configuration found. Let's define boxes on a webcam frame.")
        detector.define_boxes_interactively()
    
    # Run the detector
    detector.run()