'''
Created on 2017.07.03

@author: Ronghua Xu        

@Function: Morphological Transformations
We will learn different morphological operations like Erosion, Dilation, Opening, Closing etc.
We will see different functions like : cv2.erode(), cv2.dilate(), cv2.morphologyEx() etc.

@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.html
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt

def Erosion():
    img = cv2.imread('../../../res/j.png')
    kernel = np.ones((5,5),np.uint8)
    erosion = cv2.erode(img,kernel,iterations = 1)
    
    plt.subplot(121),plt.imshow(img),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(erosion),plt.title('Erosion')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Erosion Test')
    plt.show()
    
def Dilation():
    img = cv2.imread('../../../res/j.png')
    kernel = np.ones((5,5),np.uint8)
    dilation = cv2.dilate(img,kernel,iterations = 1)
    
    plt.subplot(121),plt.imshow(img),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(dilation),plt.title('Dilation')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Dilation Test')
    plt.show()
    
def Opening():
    img = cv2.imread('../../../res/j_opening.png')
    kernel = np.ones((5,5),np.uint8)
    opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    
    plt.subplot(121),plt.imshow(img),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(opening),plt.title('Opening')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Opening Test')
    plt.show()
    
def Closing():
    img = cv2.imread('../../../res/j_closing.png')
    kernel = np.ones((5,5),np.uint8)
    closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    
    plt.subplot(121),plt.imshow(img),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(closing),plt.title('Closing')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Closing Test')
    plt.show()
    
def Gradient():
    img = cv2.imread('../../../res/j.png')
    kernel = np.ones((5,5),np.uint8)
    gradient = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)
    
    plt.subplot(121),plt.imshow(img),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(gradient),plt.title('Gradient')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Gradient Test')
    plt.show()
    
def  TopHat():
    img = cv2.imread('../../../res/j.png')
    kernel = np.ones((5,5),np.uint8)
    tophat = cv2.morphologyEx(img, cv2.MORPH_TOPHAT, kernel)
    
    plt.subplot(121),plt.imshow(img),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(tophat),plt.title('Top Hat')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Top Hat')
    plt.show()
    
def  BlackHat():
    img = cv2.imread('../../../res/j.png')
    kernel = np.ones((5,5),np.uint8)
    blackhat = cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, kernel)
    
    plt.subplot(121),plt.imshow(img),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(blackhat),plt.title('Black Hat')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Black Hat')
    plt.show()
    
if __name__ == '__main__':
    Erosion()
    Dilation()
    Opening()
    Closing()
    Gradient()
    TopHat()
    BlackHat()
    