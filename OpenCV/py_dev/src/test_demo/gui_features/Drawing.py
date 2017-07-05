'''
Created on 2017.06.28

@author: Ronghua Xu        

@Function: Drawing Functions in OpenCV
Learn to draw different geometric shapes with OpenCV
You will learn these functions : cv2.line(), cv2.circle() , cv2.rectangle(), cv2.ellipse(), cv2.putText() etc.

@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_drawing_functions/py_drawing_functions.html#drawing-functions
'''

import numpy as np
import cv2

def test_drawing():
    # Create a black image
    img = np.zeros((512,512,3), np.uint8)
    
    '''=================Drawing Line====================='''
    # Draw a diagonal blue line with thickness of 5 px
    img = cv2.line(img,(0,0),(511,511),(255,0,0),5)
    
    '''=================Drawing Rectangle================'''
    img = cv2.rectangle(img,(384,0),(510,128),(0,255,0),3)
    
    '''=================Drawing Circle==================='''
    img = cv2.circle(img,(447,63), 63, (0,0,255), -1)
    
    '''=================Drawing Ellipse=================='''
    img = cv2.ellipse(img,(256,256),(100,50),0,0,180,255,-1)
    
    '''=================Drawing Polygon=================='''
    pts = np.array([[10,5],[20,30],[70,20],[50,10]], np.int32)
    pts = pts.reshape((-1,1,2))
    img = cv2.polylines(img,[pts],True,(0,255,255))
    
    '''=================Adding Text to Images====================='''
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img,'OpenCV',(10,500), font, 4,(255,255,255),2,cv2.LINE_AA)
    
    #Show image
    cv2.namedWindow("Drawing")   
    cv2.imshow("Drawing", img)   
    cv2.waitKey (0)  
    cv2.destroyAllWindows()

def nothing(x):
    pass

def TrackbarColorPalette():
    # Create a black image, a window
    img = np.zeros((300,512,3), np.uint8)
    cv2.namedWindow('image')
    
    # create trackbars for color change
    cv2.createTrackbar('R','image',0,255,nothing)
    cv2.createTrackbar('G','image',0,255,nothing)
    cv2.createTrackbar('B','image',0,255,nothing)
    
    # create switch for ON/OFF functionality
    switch = '0 : OFF \n1 : ON'
    cv2.createTrackbar(switch, 'image',0,1,nothing)
    
    while(1):
        cv2.imshow('image',img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
    
        # get current positions of four trackbars
        r = cv2.getTrackbarPos('R','image')
        g = cv2.getTrackbarPos('G','image')
        b = cv2.getTrackbarPos('B','image')
        s = cv2.getTrackbarPos(switch,'image')
    
        if s == 0:
            img[:] = 0
        else:
            img[:] = [b,g,r]
    
    cv2.destroyAllWindows()

if __name__ == '__main__':
    test_drawing()
    TrackbarColorPalette()
