from imutils.perspective import four_point_transform # type: ignore
from imutils import contours # type: ignore
import imutils
import cv2
from PIL import Image
from PIL import ImageFont, ImageDraw, Image
import numpy as np

DIGITS_LOOKUP = {
	(1, 1, 1, 0, 1, 1, 1): 0,
	(0, 0, 1, 0, 0, 1, 0): 1,
	(1, 0, 1, 1, 1, 1, 0): 2,
	(1, 0, 1, 1, 0, 1, 1): 3,
	(0, 1, 1, 1, 0, 1, 0): 4,
	(1, 1, 0, 1, 0, 1, 1): 5,
	(1, 1, 0, 1, 1, 1, 1): 6,
	(1, 0, 1, 0, 0, 1, 0): 7,
	(1, 1, 1, 1, 1, 1, 1): 8,
	(1, 1, 1, 1, 0, 1, 1): 9
}


image = cv2.imread('thermostat.jpg')
dimension = image.shape
height = dimension[0]
width = dimension [1]
cropped_image = image[250:(height - 505), 282:(width - 232)]

#Save the cropped image
cv2.imwrite('cropped_image.jpg', cropped_image)

gray_cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
cv2.imwrite('gray_cropped_image.jpg', gray_cropped_image)

#Crop digit number 1
digit1 = gray_cropped_image[55:115, 48:85 ]   #[height, width]
cv2.imwrite('digit1.jpg', digit1)

#Crop digit number 2
digit2 = gray_cropped_image[55:115, 48+50:85+47]   #[height, width]
cv2.imwrite('digit2.jpg', digit2)

#Crop digit number 3
digit3 = gray_cropped_image[55:115, 143:174]   #[height, width]
cv2.imwrite('digit3.jpg', digit3)

# threshold the warped image, then apply a series of morphological
# operations to cleanup the thresholded image
thresh0 = cv2.threshold(digit1, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
thresh = cv2.morphologyEx(thresh0, cv2.MORPH_OPEN, kernel)

thresh2 = cv2.threshold(digit2, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
threshImage2 = cv2.morphologyEx(thresh2, cv2.MORPH_OPEN, kernel)

thresh3 = cv2.threshold(digit3, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
threshImage3 = cv2.morphologyEx(thresh3, cv2.MORPH_OPEN, kernel)

ROI = thresh.shape
roiH = ROI[0]
roiW = ROI[1]
dW = int(roiW * 0.25)
dH = int (roiH * 0.13)
dHC = int(roiH * 0.05) #for center bar 

ROI2 = threshImage2.shape
roiH2 = ROI2[0]
roiW2 = ROI2[1]
dW2 = int(roiW2 * 0.25)
dH2 = int (roiH2 * 0.13)
dHC2= int(roiH2 * 0.05) #for center bar 

ROI3 = threshImage3.shape
roiH3 = ROI3[0]
roiW3 = ROI3[1]
dW3 = int(roiW3 * 0.25)
dH3 = int (roiH3 * 0.13)
dHC3= int(roiH3 * 0.05) #for center bar


# define the set of 7 segments
segments = [
            ((0, 0), (roiW, dH)),	# top
            ((0, 0), (dW, roiH // 2)),	# top-left
            ((roiW - dW, 0), (roiW, roiH // 2)),	# top-right
            ((0, (roiH // 2) - dHC) , (roiW, (roiH // 2) + dHC)), # center
            ((0, roiH // 2), (dW, roiH)),	# bottom-left
            ((roiW - dW, roiH // 2), (roiW, roiH)),	# bottom-right
            ((0, roiH - dH), (roiW, roiH))	# bottom
            ]

on = [0] * len(segments)

segments2 = [
            ((0, 0), (roiW2, dH2)),	# top
            ((0, 0), (dW3, roiH2 // 2)),	# top-left
            ((roiW2 - dW3, 0), (roiW2, roiH2 // 2)),	# top-right
            ((0, (roiH2 // 2) - dHC2) , (roiW2, (roiH2 // 2) + dHC2)), # center
            ((0, roiH2 // 2), (dW3, roiH2)),	# bottom-left
            ((roiW2 - dW3, roiH2 // 2), (roiW2, roiH2)),	# bottom-right
            ((0, roiH2 - dH2), (roiW2, roiH2))	# bottom
            ]

on2 = [0] * len(segments2)

segments3 = [
            ((0, 0), (roiW3, dH3)),	# top
            ((0, 0), (dW3, roiH3 // 2)),	# top-left
            ((roiW3 - dW3, 0), (roiW3, roiH3 // 2)),	# top-right
            ((0, (roiH3 // 2) - dHC3) , (roiW3, (roiH3 // 2) + dHC3)), # center
            ((0, roiH3 // 2), (dW3, roiH3)),	# bottom-left
            ((roiW3 - dW3, roiH3 // 2), (roiW3, roiH3)),	# bottom-right
            ((0, roiH3 - dH3), (roiW2, roiH3))	# bottom
            ]

on3 = [0] * len(segments3)


digits = []

# cv2.rectangle(digit1, (0, roiH - dH), (roiW, roiH), (255,0,0), 1)
# cv2.rectangle(thresh, (0, roiH - dH), (roiW, roiH), (255,0,0), 1)

# loop over the segments
for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
	# extract the segment ROI, count the total number of
	# thresholded pixels in the segment, and then compute
	# the area of the segment
	segROI = thresh[yA:yB, xA:xB]
	total = cv2.countNonZero(segROI)
	area = (xB - xA) * (yB - yA)
	# if the total number of non-zero pixels is greater than
	# 50% of the area, mark the segment as "on"
	if total / float(area) > 0.5:
		on[i]= 1
	# lookup the digit and draw it on the image

for (i, ((xA, yA), (xB, yB))) in enumerate(segments2):
	# extract the segment ROI, count the total number of
	# thresholded pixels in the segment, and then compute
	# the area of the segment
	segROI = threshImage2[yA:yB, xA:xB]
	total = cv2.countNonZero(segROI)
	area = (xB - xA) * (yB - yA)
	# if the total number of non-zero pixels is greater than
	# 50% of the area, mark the segment as "on"
	if total / float(area) > 0.5:
		on2[i]= 1
	# lookup the digit and draw it on the image

for (i, ((xA, yA), (xB, yB))) in enumerate(segments3):
	# extract the segment ROI, count the total number of
	# thresholded pixels in the segment, and then compute
	# the area of the segment
	segROI = threshImage3[yA:yB, xA:xB]
	total = cv2.countNonZero(segROI)
	area = (xB - xA) * (yB - yA)
	# if the total number of non-zero pixels is greater than
	# 50% of the area, mark the segment as "on"
	if total / float(area) > 0.5:
		on3[i]= 1
	# lookup the digit and draw it on the image

print('1st digit: ', on)
print('2nd digit: ', on2)
print('3rd digit: ', on3)
digit = DIGITS_LOOKUP[tuple(on)]
digit2 = DIGITS_LOOKUP[tuple(on2)]
digit3 = DIGITS_LOOKUP[tuple(on3)]
# digits.append(digit)
print('The corresponding digit is: ',digit)
print('The corresponding digit2 is: ',digit2)
print('The corresponding digit3 is: ',digit3)

cv2.rectangle(cropped_image, (48, 55), (48 + 30, 114), (0, 255, 0), 1)
cv2.putText(cropped_image, str(digit), (48 - 10, 55 - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

cv2.rectangle(cropped_image, (97, 55), (132, 114), (0, 255, 0), 1)
cv2.putText(cropped_image, str(digit2), (97 - 10, 55 - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)


cv2.rectangle(cropped_image, (146, 55), (174, 114), (0, 255, 0), 1)
cv2.putText(cropped_image, str(digit3), (146 - 10, 55 - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)


cv2.imshow('Final', cropped_image)

# cv2.imshow('Image',image)
cv2.imshow('Thresh Image', thresh)
cv2.imshow('Thresh Image 2', threshImage2)
cv2.imshow('Thresh Image 3', threshImage3)
cv2.waitKey(0)
cv2.destroyAllWindows()