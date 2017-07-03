'''
Created on 2017.06.28

@author: Ronghua Xu        
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt

'''
@Function: Canny Edge Detection
Concept of Canny edge detection
OpenCV functions for that : cv2.Canny()
@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_canny/py_canny.html#canny
'''

def CannyEdgeDetection():
    img = cv2.imread('../../../res/kobe.bmp',0)
    edges = cv2.Canny(img,100,200)
    
    plt.subplot(121),plt.imshow(img,cmap = 'gray')
    plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(edges,cmap = 'gray')
    plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
    
    plt.show()

if __name__ == '__main__':
    CannyEdgeDetection()
