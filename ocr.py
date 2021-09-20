import numpy as np
import cv2
import math
from scipy import ndimage
import pytesseract
import json

IMAGE_FILE_LOCATION = "D:/IMG/cvCapture/816.png" 
input_img = cv2.imread(IMAGE_FILE_LOCATION) 
ocrEncoderText = '--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-abcdefghijklmnopqrstuvwxyz'
ocrEncoderNum = '--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789'


def loadJsonObj():
    jsonLoadFile = open("roi.json")
    coordinates = json.load(jsonLoadFile)
    p1_x1 = coordinates["roi"][0]["pos_1"]["x1"]
    p1_x2 = coordinates["roi"][0]["pos_1"]["x2"]
    p1_y1 = coordinates["roi"][0]["pos_1"]["y1"]
    p1_y2 = coordinates["roi"][0]["pos_1"]["y2"]
    p2_x1 = coordinates["roi"][0]["pos_2"]["x1"]
    p2_x2 = coordinates["roi"][0]["pos_2"]["x2"]
    p2_y1 = coordinates["roi"][0]["pos_2"]["y1"]
    p2_y2 = coordinates["roi"][0]["pos_2"]["y2"]
    jsonLoadFile.close()
    return p1_x1,p1_x2,p1_y1,p1_y2,p2_x1,p2_x1,p2_x2,p2_y1,p2_y2


def region_of_interest_image(_image,_x1,_y1,_x2,_y2):
    image_copy = _image.copy()
    region_of_interest_image = image_copy[_y1:_y2, _x1:_x2]
    cv2.rectangle(_image, (_x1, _y1),(_x2, _y2), (0,0,255), 1)
    return region_of_interest_image,_image

def main(input_img):
    p1_x1,p1_x2,p1_y1,p1_y2,p2_x1,p2_x1,p2_x2,p2_y1,p2_y2 = loadJsonObj()
    image = input_img
    ROI1,image = region_of_interest_image(image,p1_x1,p1_y1,p1_x2,p1_y2)
    ROI2,image = region_of_interest_image(image,p2_x1,p2_y1,p2_x2,p2_y2)
    Part = pytesseract.image_to_string(ROI1,config = ocrEncoderText)
    Part = Part.rstrip()
    zone = pytesseract.image_to_string(ROI2,config = ocrEncoderNum)
    zone = zone.rstrip()
    print("Part: "+Part+" Zone: "+zone)
    return image,Part,zone

if __name__ == "__main__":
    main(input_img)
    #cv2.waitKey(0)


    