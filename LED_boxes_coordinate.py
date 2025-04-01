import cv2
import numpy as np
import time
import os

def main():
    # LED box coordinates [x, y, width, height], x and y of top-left corner
    led_box_coordinates = [
        [36, 259, 40+10, 40+10],
        [40, 319, 36+10, 33+10],
        [45, 373, 40+10, 34+10]
    ]
    
    # Define box colors (BGR format)
    box_colors = [
        (0, 0, 255),    # Red
        (0, 255, 0),    # Green
        (255, 0, 0)     # Blue
    ]
    
    # Create output directory if it doesn't exist
    output_dir = "webcam_frames"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Initialize webcam
    cap = cv2.VideoCapture(2)
    
    # Check if the webcam is opened correctly
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    print("Webcam initialized. Press Ctrl+C to quit.")
    print(f"Saving frames to {output_dir}/ directory")
    
    frame_count = 0
    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            
            # If frame is read correctly ret is True
            if not ret:
                print("Error: Can't receive frame. Exiting...")
                break
            
            # Draw the LED boxes on the frame
            for i, (x, y, w, h) in enumerate(led_box_coordinates):
                # Draw rectangle
                cv2.rectangle(frame, (x, y), (x + w, y + h), box_colors[i], 2)
                
                # Add box label
                cv2.putText(frame, f"Box {i+1}", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_colors[i], 2)
            
            # Save the frame to file
            frame_path = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            
            # Print update every 10 frames
            if frame_count % 10 == 0:
                print(f"Saved frame {frame_count} to {frame_path}")
            
            frame_count += 1
            
            # Brief pause to control frame rate
            time.sleep(0.1)  # Adjust this for faster/slower capture
            
    except KeyboardInterrupt:
        print("\nCapture stopped by user")
    
    # Release the capture
    cap.release()
    print(f"Captured {frame_count} frames. Frames saved to {output_dir}/ directory.")

if __name__ == "__main__":
    main()