import cv2
import pytesseract

# Load the image

image = cv2.imread('thermometer.png')

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply some preprocessing
gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

# Use pytesseract to extract text
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789.C°'  # only digits, decimal point, and Celsius symbol
text = pytesseract.image_to_string(gray, config=custom_config)

# Clean up the extracted text
text = text.strip()

print(f"Extracted Temperature: {text}")
