import cv2
import numpy as np
from easyocr import Reader
from PIL import Image as PilImage, ImageDraw, ImageFont

class OCRProcessor:
    def __init__(self):
        self.reader = Reader(['en', 'pt'], gpu=True)

    def run_ocr(self, image_path):
        img = cv2.imread(image_path)  
        result = self.reader.readtext(img)
        extracted_text = ""
        for (box, text, probability) in result:
            lt, rt, br, bl = self.box_coordinates(box)
            img = self.draw_img(img, lt, br, text)
            extracted_text += f"{text}\n"
        return img, extracted_text
    
    def run_ocr_simple(self, image_path):
        img = cv2.imread(image_path)  
        result = self.reader.readtext(img, detail=0)

        return result
       
    def box_coordinates(self, box):
        (lt, rt, br, bl) = box
        lt = (int(lt[0]), int(lt[1]))
        rt = (int(rt[0]), int(rt[1]))
        br = (int(br[0]), int(br[1]))
        bl = (int(bl[0]), int(bl[1]))
        return lt, rt, br, bl

    def draw_img(self, img, lt, br, text, font_path='EasyOCR-master/calibri.ttf', color=(200, 255, 0), thickness=2, font_size=22):
        cv2.rectangle(img, lt, br, color, thickness)
        font = ImageFont.truetype(font_path, font_size)
        img_pil = PilImage.fromarray(img)
        draw = ImageDraw.Draw(img_pil)
        draw.text((lt[0], lt[1] - font_size), text, font=font, fill=color)
        img = np.array(img_pil)
        return img
