from paddleocr import PaddleOCR

# Configuration
image_path = "/home/billy/GUI/SnapShotImages/processed_snapshot_simple20241031_152828.jpg"
# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Perform OCR
result = ocr.ocr(image_path, cls=True)

print(result)
