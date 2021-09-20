# Importing necessary libraries
import json
import numpy as np
import cv2
import math
from scipy import ndimage
import pytesseract

input_img = cv2.imread('_T.jpg')
ocrEncoder = '--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
coordinates = [] 
image = input_img

def shape_selection(event, x, y, flags, param): 
    # making coordinates global
    global coordinates 
    global image
    # Storing the (x1,y1) coordinates when left mouse button is pressed  
    if event == cv2.EVENT_LBUTTONDOWN: 
        coordinates = [(x, y)] 
    # Storing the (x2,y2) coordinates when the left mouse button is released and make a rectangle on the selected region
    elif event == cv2.EVENT_LBUTTONUP: 
        coordinates.append((x, y)) 
        # Drawing a rectangle around the region of interest (roi)
        print(coordinates[0][0])
        print(coordinates[0][1])
        print(coordinates[1][0])
        print(coordinates[1][1])
        cv2.rectangle(image, coordinates[0], coordinates[1], (0,0,255), 1) 
        cv2.imshow("image", image) 
  
  
def saveJson(_key):
    if(_key == 0):
        with open('roi.json', 'r+') as f:
                json_data = json.load(f)
                json_data["roi"][0]["pos_1"]["x1"] = coordinates[0][0]
                json_data["roi"][0]["pos_1"]["y1"] = coordinates[0][1]
                json_data["roi"][0]["pos_1"]["x2"] = coordinates[1][0]
                json_data["roi"][0]["pos_1"]["y2"] = coordinates[1][1]
                f.seek(0)
                f.write(json.dumps(json_data))
                f.truncate()
    else:
         with open('roi.json', 'r+') as f:
                json_data = json.load(f)
                json_data["roi"][0]["pos_2"]["x1"] = coordinates[0][0]
                json_data["roi"][0]["pos_2"]["y1"] = coordinates[0][1]
                json_data["roi"][0]["pos_2"]["x2"] = coordinates[1][0]
                json_data["roi"][0]["pos_2"]["y2"] = coordinates[1][1]
                f.seek(0)
                f.write(json.dumps(json_data))
                f.truncate()
            
def main(_key):
    if(_key == 0):
        print("part")
    else:
        print("zone")
        
    global image
    image_copy = image.copy()
    cv2.namedWindow("image") 
    cv2.setMouseCallback("image", shape_selection) 
    while True: 
        cv2.imshow("image", image) 
        key = cv2.waitKey(1) & 0xFF
        if key==13: # If 'enter' is pressed, apply OCR
            break
        if key == ord("c"): # Clear the selection when 'c' is pressed 
            image = image_copy.copy() 
    
    if len(coordinates) == 2: 
        image_roi = image_copy[coordinates[0][1]:coordinates[1][1], 
                                coordinates[0][0]:coordinates[1][0]] 
        cv2.imshow("Selected Region of Interest - Press any key to proceed", image_roi) 
        text = pytesseract.image_to_string(image_roi,config = ocrEncoder)
        text = text.rstrip()
        print("The text in the selected region is as follows:")
        print(text)
        saveJson(_key)
        jsonLoadFile = open("roi.json")
        jsoncoordinates = json.load(jsonLoadFile)
        print(jsoncoordinates)
        jsonLoadFile.close()
        cv2.waitKey(0)
    cv2.destroyWindow('image') 
    cv2.destroyWindow('Selected Region of Interest - Press any key to proceed') 
    return True

if __name__ == "__main__":
    main(1)

