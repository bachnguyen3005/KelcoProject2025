from paddleocr import PaddleOCR

class OCRProcessor:
    def __init__(self):
        # Initialize PaddleOCR with English language and angle classification enabled
        self.reader = PaddleOCR(
            use_angle_cls=True, 
            lang='en', show_log = False, 
            det_dn_thresh=0.3,
            det_db_box_thresh=0.3,
            det_db_unclip_ratio=1.8,
            use_gpu = True,
            det_model_dir = 'ch_PP-OCRv4_det_infer',
            rec_model_dir = 'ch_PP-OCRv4_rec_infer')                  
        
    def extract_numbers(self, image_path):
        result = self.reader.ocr(image_path, det=True, rec=True, cls=False)
        detected_texts = [res[1][0] for res in result[0]]
        print(detected_texts)
        
        numbers_only = []
        for text in detected_texts:
            # Skip 'kPa' since it's not a number we want
            if text == 'kPa':
                continue
                
            # Handle case where number has leading zeros (like '0451')
            if text.isdigit():
                numbers_only.append(int(text))
                continue
                
            # Handle case where text and numbers are combined (like 'Cal031')
            import re
            numeric_parts = re.findall(r'\d+', text)
            for num_str in numeric_parts:
                numbers_only.append(int(num_str))
        
        print(numbers_only)
        if len(numbers_only) == 2:
            return numbers_only
        
        # If the expected numbers weren't found, return "ERROR"
        return "ERROR"
    
    
    def extract_text(self, image_path):
        """
        Extract only text (non-numeric parts) from the detected text in the image.
        """
        result = self.reader.ocr(image_path, det = True, rec = True, cls=False)
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
        result = self.reader.ocr(image_path, det = True, rec = True, cls=False)
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
