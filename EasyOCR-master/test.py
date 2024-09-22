from easyocr import Reader
import cv2
import matplotlib.pyplot as plt 
from PIL import ImageFont, ImageDraw, Image
import numpy as np

font = 'calibri.ttf'
gpu = True


#Read the image
img = cv2.imread('snapshot.jpg')

original = img.copy()

#Text recognition
reader = Reader(['en', 'pt'],gpu)

result = reader.readtext(img)

#Write title 
def write_text(text, x, y, img, font, color=(50,50,255), font_size=22):
  font = ImageFont.truetype(font, font_size)
  img_pil = Image.fromarray(img)
  draw = ImageDraw.Draw(img_pil)
  draw.text((x - font_size, y), text, font = font, fill = color)
  img = np.array(img_pil)
  return img

#Draw the bounding box
#lt = left top
#rt = right top
#br = bottom right
#bl = bottom left
def box_coordinates(box):
  (lt, rt, br, bl) = box
  lt = (int(lt[0]), int(lt[1]))
  rt = (int(rt[0]), int(rt[1]))
  br = (int(br[0]), int(br[1]))
  bl = (int(bl[0]), int(bl[1]))
  return lt, rt, br, bl

#draw_img function
def draw_img(img, lt, br, color=(200,255,0),thickness=2):
  cv2.rectangle(img, lt, br, color, thickness)
  return img


img = original.copy()
for (box, text, probability) in result:
  print(box, text, probability)
  lt, rt, br, bl = box_coordinates(box)
  img = draw_img(img, lt, br)
  img = write_text(text, lt[0], lt[1], img, font)
cv2.imshow("Text detected image",img)
cv2.waitKey(0)
cv2.destroyAllWindows()









