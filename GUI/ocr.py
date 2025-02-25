from paddleocr import PaddleOCR

class OCRProcessor:
    def __init__(self):
        # Initialize PaddleOCR with English language and angle classification enabled
        self.reader = PaddleOCR(use_angle_cls=True, lang='en')

    def extract_numbers(self, image_path):
            
            result = self.reader.ocr(image_path, cls=True)
            detected_texts = [res[1][0] for res in result[0]]
            print(detected_texts)
            numbers_only = []

            for text in detected_texts:
                parts = text.split()
                for part in parts:
                    try:
                        number = int(part)
                        numbers_only.append(number)
                    except ValueError:
                        pass  # Ignore non-numeric part

                # Check if there are exactly two numeric elements
                print(numbers_only)
                if len(numbers_only) == 2:

                    return numbers_only

            # If the loop completes without finding exactly two numbers, return "ERROR"
            return "ERROR"                    

    def extract_text(self, image_path):
        """
        Extract only text (non-numeric parts) from the detected text in the image.
        """
        result = self.reader.ocr(image_path, cls=True)
        detected_texts = [res[1][0] for res in result[0]]
        text_only = []

        for text in detected_texts:
            parts = text.split()
            for part in parts:
                if not part.isdigit():
                    text_only.append(part)

        return text_only

    def get_lock_status(self, image_path):
        """
        Determine if the detected text indicates 'UNLOCKED' or 'LOCKED'.
        """
        # Perform OCR
        result = self.reader.ocr(image_path, cls=True)
        print(result)
            # Check if OCR result is None or empty
    # Check if OCR result is None, not a list, or empty
        if not result or not isinstance(result, list) or len(result) == 0:
            print("No text detected or OCR failed.")
            return "UNKNOWN"
        # Check if the result[0] is valid and contains detected texts
        if not result[0] or not isinstance(result[0], list):
            print("Invalid OCR output structure.")
            return "UNKNOWN"
            
        detected_texts = [res[1][0] for res in result[0]]  # Extract text parts

        # Check the first character of the detected text
        for text in detected_texts:
            if text.startswith('L'):
                print("LOCKED")
                return "LOCKED"
            else:
                return "UNLOCKED"

        # Default to "UNKNOWN" if no valid text is found
        return "UNKNOWN"
