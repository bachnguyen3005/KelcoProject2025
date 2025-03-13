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