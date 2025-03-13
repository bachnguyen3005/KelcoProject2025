import cv2
import numpy as np
import matplotlib.pyplot as plt
import time
import os

def detect_blinking_led(video_path, led_position, threshold=100):
    """
    Detect if an LED at a specified position is blinking in a WebM video.
    Headless version - no display windows, just analysis and plots.
    
    Args:
        video_path (str): Path to the WebM video file
        led_position (list): Position of the LED as [x, y, width, height]
        threshold (int): Brightness threshold to consider LED as ON
    
    Returns:
        dict: Results containing blink data
    """
    # Check if file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return None
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Check if video opened successfully
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}. Make sure OpenCV is compiled with WebM support.")
        return None
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    
    print(f"Video loaded: {frame_count} frames, {fps} fps, {duration:.2f} seconds")
    print(f"Analyzing LED at position {led_position}")
    
    # Unpack LED position
    x, y, w, h = led_position
    
    # Arrays to store brightness values and LED states over time
    frame_times = []
    brightness_values = []
    led_states = []
    
    # Create a directory for frame snapshots
    snapshot_dir = "led_snapshots"
    os.makedirs(snapshot_dir, exist_ok=True)
    
    # Variables to track blinking
    blinks = 0
    last_state = False
    blink_frames = []  # Store frame numbers where blinks occur
    
    # Time tracking
    start_time = time.time()
    processed_frames = 0
    
    # Process each frame
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Get current frame timestamp
        frame_time = processed_frames / fps if fps > 0 else processed_frames / 30
        frame_times.append(frame_time)
        
        # Ensure coordinates are within frame boundaries
        frame_height, frame_width = frame.shape[:2]
        x_bounded = max(0, min(x, frame_width - 1))
        y_bounded = max(0, min(y, frame_height - 1))
        w_bounded = min(w, frame_width - x_bounded)
        h_bounded = min(h, frame_height - y_bounded)
        
        # Extract the ROI for the specified LED
        roi = frame[y_bounded:y_bounded+h_bounded, x_bounded:x_bounded+w_bounded]
        
        if roi.size == 0:
            print(f"Warning: ROI is empty at frame {processed_frames}. Check the LED position coordinates.")
            brightness = 0
        else:
            # Convert to HSV for better color and brightness analysis
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Calculate brightness (mean of V channel)
            brightness = np.mean(hsv_roi[:,:,2])
        
        brightness_values.append(brightness)
        
        # Determine if LED is ON
        is_on = brightness > threshold
        led_states.append(1 if is_on else 0)
        
        # Check for state change (blinking)
        if processed_frames > 0 and is_on != last_state:
            if is_on:  # Only count transitions from OFF to ON
                blinks += 1
                blink_frames.append(processed_frames)
                
                # Save a snapshot of this frame
                snapshot_path = os.path.join(snapshot_dir, f"blink_{blinks}_frame_{processed_frames}.jpg")
                
                # Draw rectangle on the frame
                display_frame = frame.copy()
                cv2.rectangle(display_frame, (x_bounded, y_bounded), 
                             (x_bounded+w_bounded, y_bounded+h_bounded), (0, 255, 0), 2)
                
                cv2.putText(display_frame, f"Blink #{blinks}", (x_bounded, y_bounded-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                cv2.imwrite(snapshot_path, display_frame)
        
        # Update last state
        last_state = is_on
        
        processed_frames += 1
        
        # Progress update for long videos
        if processed_frames % 100 == 0 or processed_frames == frame_count:
            elapsed = time.time() - start_time
            frames_per_second = processed_frames / elapsed
            remaining_frames = frame_count - processed_frames if frame_count > 0 else 0
            remaining_time = remaining_frames / frames_per_second if frames_per_second > 0 else 0
            
            print(f"Processed {processed_frames}/{frame_count} frames ({100*processed_frames/frame_count:.1f}%) - ETA: {remaining_time:.1f}s")
            print(f"Current blinks detected: {blinks}")
    
    # Calculate blink rate
    duration = processed_frames / fps if fps > 0 else processed_frames / 30
    blink_rate = blinks / duration if duration > 0 else 0
    
    # Close the video
    cap.release()
    
    # Prepare results
    results = {
        'video_path': video_path,
        'led_position': led_position,
        'total_frames': processed_frames,
        'duration': duration,
        'blinks_detected': blinks,
        'blink_rate': blink_rate,
        'brightness_values': brightness_values,
        'led_states': led_states,
        'frame_times': frame_times,
        'blink_frames': blink_frames
    }
    
    # Generate blink pattern visualization
    plot_blink_pattern(results)
    
    # Generate a sample snapshots montage if there are blinks
    if blinks > 0:
        create_blink_montage(snapshot_dir, results)
    
    # Print summary
    print("\nBlink Detection Results:")
    print(f"LED at position {led_position}")
    print(f"Video duration: {duration:.2f} seconds")
    print(f"Blinks detected: {blinks}")
    print(f"Blink rate: {blink_rate:.2f} Hz ({blink_rate*60:.1f} blinks per minute)")
    
    if blinks > 0:
        # Calculate average blink interval
        blink_intervals = calculate_blink_intervals(led_states, frame_times)
        avg_interval = np.mean(blink_intervals) if blink_intervals else 0
        print(f"Average blink interval: {avg_interval*1000:.1f} ms")
        
        # Show blink frames
        print("\nBlinks detected at frames:", blink_frames)
        
        print("\n✅ VERIFICATION: LED is blinking")
        print(f"Snapshots of each blink have been saved to the '{snapshot_dir}' directory")
    else:
        print("\n❌ VERIFICATION: LED is NOT blinking")
    
    return results

def plot_blink_pattern(results):
    """Generate plots showing the LED blinking pattern"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Plot brightness values
    ax1.plot(results['frame_times'], results['brightness_values'])
    ax1.axhline(y=100, color='r', linestyle='--', alpha=0.7)  # Threshold line
    ax1.set_title('LED Brightness Over Time')
    ax1.set_xlabel('Time (seconds)')
    ax1.set_ylabel('Brightness')
    ax1.grid(True, alpha=0.3)
    
    # Plot ON/OFF states
    ax2.step(results['frame_times'], results['led_states'], where='post')
    ax2.set_title('LED ON/OFF State Over Time')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('State (1=ON, 0=OFF)')
    ax2.set_ylim(-0.1, 1.1)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('led_blink_analysis.png')
    print("\nSaved brightness and state plots to 'led_blink_analysis.png'")

def calculate_blink_intervals(led_states, frame_times):
    """Calculate time intervals between blinks"""
    blink_times = []
    
    # Find all OFF to ON transitions (blink starts)
    for i in range(1, len(led_states)):
        if led_states[i-1] == 0 and led_states[i] == 1:
            blink_times.append(frame_times[i])
    
    # Calculate intervals between consecutive blinks
    intervals = []
    for i in range(1, len(blink_times)):
        intervals.append(blink_times[i] - blink_times[i-1])
    
    return intervals

def create_blink_montage(snapshot_dir, results):
    """Create a montage of blink snapshots if available"""
    try:
        import matplotlib.gridspec as gridspec
        
        # Get a list of all snapshot files
        snapshot_files = [f for f in os.listdir(snapshot_dir) if f.startswith('blink_') and f.endswith('.jpg')]
        
        # Sort by blink number
        snapshot_files.sort(key=lambda x: int(x.split('_')[1]))
        
        # Limit to first 9 blinks for display
        snapshot_files = snapshot_files[:min(9, len(snapshot_files))]
        
        if not snapshot_files:
            return
        
        # Create a grid for displaying snapshots
        rows = int(np.ceil(len(snapshot_files) / 3))
        cols = min(3, len(snapshot_files))
        
        fig = plt.figure(figsize=(12, 4 * rows))
        grid = gridspec.GridSpec(rows, cols)
        
        for i, filename in enumerate(snapshot_files):
            img = cv2.imread(os.path.join(snapshot_dir, filename))
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            ax = plt.subplot(grid[i])
            ax.imshow(img_rgb)
            ax.set_title(f"Blink #{i+1}")
            ax.axis('off')
        
        plt.tight_layout()
        plt.savefig('blink_snapshots.png')
        print("Saved blink snapshots montage to 'blink_snapshots.png'")
    except Exception as e:
        print(f"Could not create blink montage: {e}")

if __name__ == "__main__":
    # Video path - update with your WebM video path
    video_path = "/home/dinh/Documents/PlatformIO/Projects/kelco_test_001/paddle_flow_test/blinking_test.webm"
    
    # Position for LED 2
    led_position = [63, 336, 27, 30]  # [x, y, width, height]
    
    print(f"Analyzing WebM video for LED blinking (headless mode)")
    print(f"Video path: {video_path}")
    
    # Ensure file exists
    if not os.path.exists(video_path):
        video_path = input("Enter the correct path to your WebM video: ")
    
    # Run the blink detection
    results = detect_blinking_led(video_path, led_position)