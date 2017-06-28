'''
Created on 2017.06.28

@author: Ronghua Xu        
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt

'''
@Function: Smoothing Images
Blur imagess with various low pass filters
Apply custom-made filters to images (2D convolution)
@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_filtering/py_filtering.html#filtering
'''

#2D Convolution ( Image Filtering )
def Convolution2D():
    img = cv2.imread('../../res/opencv-logo-black.png')

    kernel = np.ones((5,5),np.float32)/25
    dst = cv2.filter2D(img,-1,kernel)
    
    plt.subplot(121),plt.imshow(img),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(dst),plt.title('Averaging')
    plt.xticks([]), plt.yticks([])
    plt.show()

#Image Blurring (Image Smoothing)
def ImageBlurring():
    img = cv2.imread('../../res/opencv-logo-black.png')
    
    #img_median = cv2.imread('../../res/opencv-logo-median.jpeg')
    
    # Averaging
    blur_Averaging = cv2.blur(img,(5,5))

    # Gaussian Filtering
    blur_Gaussian = cv2.GaussianBlur(img,(5,5),0)

    #Median Filtering
    blur_Median = cv2.medianBlur(img,5)
    
    plt.subplot(221),plt.imshow(img),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(222),plt.imshow(blur_Averaging),plt.title('Blurred-Averaging')
    plt.xticks([]), plt.yticks([])
    plt.subplot(223),plt.imshow(blur_Gaussian),plt.title('Blurred-Gaussian')
    plt.xticks([]), plt.yticks([])
    plt.subplot(224),plt.imshow(blur_Median),plt.title('Blurred-Median')
    plt.xticks([]), plt.yticks([])
    
    plt.show()
    
if __name__ == '__main__':
    #Convolution2D()
    ImageBlurring()
    