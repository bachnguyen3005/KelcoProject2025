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
        import re
        
        result = self.reader.ocr(image_path, det=True, rec=True, cls=False)
        detected_texts = [res[1][0] for res in result[0]]
        print(f"Detected texts: {detected_texts}")
        
        numbers_only = []
        for text in detected_texts:
            # Handle kPa cases (both with and without space)
            if text.startswith('kPa'):
                # Extract digits after 'kPa', removing any spaces
                num_part = text[3:].strip()
                if num_part.isdigit():
                    numbers_only.append(int(num_part))
                    continue
            
            # Handle 'Cal' vs 'Ca1' OCR mistake (with or without space)
            if text.startswith('Ca1'):
                # Remove the 'Ca1' prefix and any spaces
                num_part = text[3:].strip()
                if num_part.isdigit():
                    numbers_only.append(int(num_part))
                    continue
                    
            # Handle normal digit-only cases
            elif text.isdigit():
                numbers_only.append(int(text))
                continue
                
            # Extract all numeric sequences as fallback
            numeric_parts = re.findall(r'\d+', text)
            for num_str in numeric_parts:
                numbers_only.append(int(num_str))
        
        print(f"Extracted numbers: {numbers_only}")
        
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
