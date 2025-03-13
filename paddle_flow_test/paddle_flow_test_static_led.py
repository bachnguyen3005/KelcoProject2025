import cv2
import numpy as np
import matplotlib.pyplot as plt

def detect_leds(image_path, box_coordinates):
    """
    Detect LEDs in specified box coordinates and determine if they are lit up and their color.
    
    Args:
        image_path (str): Path to the image file
        box_coordinates (list): List of boxes defined as [x, y, width, height]
    
    Returns:
        list: Status of each box containing LED information
    """
    # Load the image
    img = cv2.imread(image_path)
    
    # Check if image was loaded successfully
    if img is None:
        print(f"Error: Could not load image from {image_path}")
        return []
    
    # Convert to RGB (OpenCV loads images in BGR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Convert to HSV for better color detection
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define color ranges in HSV
    color_ranges = {
        'green': (np.array([40, 70, 70]), np.array([90, 255, 255])),
        'red1': (np.array([0, 100, 100]), np.array([10, 255, 255])),  # Red wraps around in HSV
        'red2': (np.array([160, 100, 100]), np.array([180, 255, 255])),  # Second part of red range
        'yellow': (np.array([20, 100, 100]), np.array([40, 255, 255])),
        'blue': (np.array([100, 100, 100]), np.array([140, 255, 255]))
    }
    
    # Create a copy for visualization
    display_img = img_rgb.copy()
    
    # Results list
    results = []
    
    # Process each box
    for i, box in enumerate(box_coordinates):
        x, y, w, h = box
        
        # Ensure coordinates are within image bounds
        x = max(0, min(x, img.shape[1]-1))
        y = max(0, min(y, img.shape[0]-1))
        w = min(w, img.shape[1] - x)
        h = min(h, img.shape[0] - y)
        
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
            
            for color_name, (lower, upper) in color_ranges.items():
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
        
        # Add text to the image
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
    
    # Display the result
    plt.figure(figsize=(12, 10))
    plt.imshow(display_img)
    plt.title('LED Detection Results')
    plt.axis('off')
    plt.savefig('led_detection_result.png')
    plt.show()
    
    # Print the results
    print("\nLED Detection Results:")
    for result in results:
        print(f"Box {result['box_id']} ({result['position']}): LED is {'ON' if result['lit'] else 'OFF'}")
        if result['lit']:
            print(f"  Color: {result['color']}")
            print(f"  Brightness: {result['brightness']:.2f}")
    
    return results

def check_green_leds(results):
    """
    Check if there are exactly two green LEDs lit up.
    
    Args:
        results (list): List of LED detection results
    
    Returns:
        bool: True if exactly 2 green LEDs are lit, False otherwise
    """
    green_leds_count = sum(1 for r in results if r['lit'] and r['color'] == 'green')
    
    if green_leds_count == 2:
        print("\n✅ VERIFICATION SUCCESSFUL: Exactly 2 green LEDs are lit up.")
        return True
    else:
        print(f"\n❌ VERIFICATION FAILED: Expected 2 green LEDs, but detected {green_leds_count}.")
        return False

if __name__ == "__main__":
    # Define the image path - update this to your image path
    image_path = "/home/dinh/Documents/PlatformIO/Projects/kelco_test_001/paddle_flow_test/flow_switch_test11.jpg"
    
    # Check if the image exists
    try:
        test_img = cv2.imread(image_path)
        if test_img is None:
            print(f"Could not load image from {image_path}")
            image_path = input("Enter the correct image path: ")
    except:
        print(f"Error loading image: {image_path}")
        image_path = input("Enter the correct image path: ")
    
    # Fixed box coordinates from your input
    box_coordinates = [
        [56,269,37,37],
        [60,329,36,33],
        [65,383,40,34]
    ]
    
    # Run LED detection
    led_results = detect_leds(image_path, box_coordinates)
    
    # Verify if exactly 2 green LEDs are lit
    verification_result = check_green_leds(led_results)
    
    print("\nDetailed Analysis:")
    lit_leds = [r for r in led_results if r['lit']]
    if lit_leds:
        print(f"Total LEDs lit: {len(lit_leds)}")
        for color in set(r['color'] for r in lit_leds):
            count = sum(1 for r in lit_leds if r['color'] == color)
            print(f"  - {color.capitalize()} LEDs: {count}")