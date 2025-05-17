import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button
import pandas as pd
import os
import json
import time
from datetime import datetime

class MatplotlibBoxDrawer:
    def __init__(self, camera_id=2, config_file="led_boxes.json", max_boxes=3):
        """Interactive box drawer for LED positions using Matplotlib"""
        self.camera_id = camera_id
        self.config_file = config_file
        self.max_boxes = max_boxes
        self.cap = None
        self.boxes = []
        self.current_box = []
        self.drawing = False
        self.temp_patches = []  # Track temporary patches
        self.box_colors = ['r', 'g', 'b', 'c', 'm', 'y']  # Colors for different boxes
        self.results_dir = "led_webcam_results"
        
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)
    
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
    
    def capture_frame(self):
        """Capture a single frame from the webcam"""
        if not self.setup_webcam():
            return None
        
        print("Capturing a snapshot from webcam...")
        
        # Capture a few frames to let the camera adjust
        for _ in range(10):
            ret, _ = self.cap.read()
            if not ret:
                print("Failed to grab frame from webcam")
                self.cap.release()
                return None
        
        # Capture the actual frame to use
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to grab frame from webcam")
            self.cap.release()
            return None
        
        # Convert to RGB for matplotlib
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Close the webcam
        self.cap.release()
        
        return frame_rgb
    
    def on_press(self, event):
        """Handle mouse button press event"""
        if event.inaxes != self.ax:
            return
        
        if len(self.boxes) >= self.max_boxes:
            print(f"Maximum {self.max_boxes} boxes allowed! Use Reset to start over.")
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
        box = [int(x), int(y), int(w), int(h)]
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
        
        # Update the DataFrame
        self.update_dataframe()
        
        self.fig.canvas.draw_idle()
    
    def update_dataframe(self):
        """Update the pandas DataFrame with current box coordinates"""
        box_data = []
        for i, box in enumerate(self.boxes):
            box_data.append({
                'Box Number': i+1,
                'X': box[0],
                'Y': box[1],
                'Width': box[2],
                'Height': box[3]
            })
        
        self.df = pd.DataFrame(box_data)
        
        # Display the DataFrame
        if not self.df.empty:
            print("\nCurrent Box Coordinates:")
            print(self.df)
    
    def reset_boxes(self, event):
        """Reset all boxes"""
        self.boxes = []
        
        # Properly remove all patches (boxes)
        for patch in self.ax.patches:
            patch.remove()
            
        # Properly remove all texts (labels)
        for text in self.ax.texts:
            text.remove()
        
        # Reset the DataFrame
        self.df = pd.DataFrame(columns=['Box Number', 'X', 'Y', 'Width', 'Height'])
        
        self.ax.set_title('Click and drag to define LED boxes (max 3)\nPress Save when done')
        self.fig.canvas.draw_idle()
        print("All boxes reset")
    
    def save_boxes(self, event):
        """Save boxes to file and close the figure"""
        if not self.boxes:
            print("No boxes defined. Please define at least one box before saving.")
            return
        
        # Save boxes to file
        with open(self.config_file, 'w') as f:
            json.dump(self.boxes, f, indent=4)
        
        print(f"Saved {len(self.boxes)} boxes to {self.config_file}")
        
        # Create a copy of the DataFrame
        df_copy = self.df.copy()
        
        # Also save as CSV
        csv_file = os.path.join(self.results_dir, "led_boxes.csv")
        df_copy.to_csv(csv_file, index=False)
        print(f"Also saved as CSV to {csv_file}")
        
        plt.close(self.fig)
    
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
    
    def setup_figure(self, frame):
        """Set up the matplotlib figure and connect event handlers"""
        self.fig, self.ax = plt.subplots(figsize=(12, 10))
        self.ax.imshow(frame)
        self.ax.set_title('Click and drag to define LED boxes (max 3)\nPress Save when done')
        
        # Initialize DataFrame
        self.df = pd.DataFrame(columns=['Box Number', 'X', 'Y', 'Width', 'Height'])
        
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
        
        # Load existing boxes if available
        if self.load_boxes():
            for i, box in enumerate(self.boxes):
                x, y, w, h = box
                # Add permanent rectangle
                rect = patches.Rectangle((x, y), w, h, linewidth=2, 
                                        edgecolor=self.box_colors[i % len(self.box_colors)], 
                                        facecolor='none')
                self.ax.add_patch(rect)
                
                # Add box number
                self.ax.text(x, y-10, f"Box {i+1}", color='white', 
                            backgroundcolor=self.box_colors[i % len(self.box_colors)],
                            fontsize=12, weight='bold')
            
            # Update DataFrame
            self.update_dataframe()
    
    def run(self):
        """Run the interactive box drawer"""
        # Capture a frame from the webcam
        frame = self.capture_frame()
        if frame is None:
            print("Failed to capture frame. Exiting.")
            return False
        
        # Setup matplotlib figure
        self.setup_figure(frame)
        
        # Show the plot
        plt.show()
        
        return True


if __name__ == "__main__":
    # Run the box drawer
    drawer = MatplotlibBoxDrawer(camera_id=2, max_boxes=3)  # Adjust camera_id if needed
    drawer.run()
