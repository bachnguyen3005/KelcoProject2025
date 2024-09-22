import cv2
import matplotlib.pyplot as plt
# Initialize the webcam
cap = cv2.VideoCapture(2)  # 0 is usually the default webcam

# Check if the webcam is opened correctly
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # If a frame was captured successfully
    if ret:
        # Display the frame in a window
        cv2.imshow('Press Space to Capture', frame)
        
        # Wait for the user to press a key
        key = cv2.waitKey(1)

        # If the space bar (ASCII 32) is pressed, capture the image
        if key == 32:  # 32 is the ASCII code for the space bar
            # Save the captured image to a file
            cv2.imwrite('captured_image.jpg', frame)
            print("Image captured and saved as 'captured_image.jpg'.")

        # If the escape key (ASCII 27) is pressed, exit the loop
        elif key == 27:  # 27 is the ASCII code for the escape key
            print("Exiting...")
            break
    else:
        print("Error: Could not capture an image.")
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
