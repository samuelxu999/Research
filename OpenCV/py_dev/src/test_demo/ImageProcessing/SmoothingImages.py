'''
Created on 2017.06.28

@author: Ronghua Xu      
  
@Function: Smoothing Images
Blur imagess with various low pass filters
Apply custom-made filters to images (2D convolution)

@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_filtering/py_filtering.html#filtering
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt


'''
@Function: 2D Convolution ( Image Filtering )
Images also can be filtered with various low-pass filters (LPF), high-pass filters (HPF), etc.
A LPF helps in removing noise, or blurring the image. 
A HPF filters helps in finding edges in an image.
'''
def Convolution2D():
    img = cv2.imread('../../../res/opencv-logo.png')

    kernel = np.ones((5,5),np.float32)/25
    dst = cv2.filter2D(img,-1,kernel)
    
    plt.subplot(121),plt.imshow(img),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(dst),plt.title('Convolution2D-Averaging')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Convolution2D')
    plt.show()

'''
@Function: Image Blurring (Image Smoothing)
Image blurring is achieved by convolving the image with a low-pass filter kernel. It is useful for removing noise.
'''
def AveragingBlurring():
    img = cv2.imread('../../../res/opencv-logo.png')
    
    # Averaging
    blur_Averaging = cv2.blur(img,(5,5))

    
    plt.subplot(121),plt.imshow(img),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(blur_Averaging),plt.title('Blurred-Averaging')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Averaging Blurring')
    plt.show()
    
def GaussianBlurring():
    img = cv2.imread('../../../res/opencv-logo.png')

    # Gaussian Filtering
    blur_Gaussian = cv2.GaussianBlur(img,(5,5),0)
    
    plt.subplot(121),plt.imshow(img),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(blur_Gaussian),plt.title('Blurred-Gaussian')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Gaussian Blurring')
    plt.show()
    
def MedianBlurring():
    img_median = cv2.imread('../../../res/opencv-logo-median.jpg')

    # Median Filtering
    blur_Median = cv2.medianBlur(img_median,5)
    
    plt.subplot(121),plt.imshow(img_median),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(blur_Median),plt.title('Blurred-Median')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Median Blurring')
    plt.show()
    
def BilateralBlurring():
    img_bilateral = cv2.imread('../../../res/bilateral.jpg')

    # Bilateral Filtering
    blur_bilateral = cv2.bilateralFilter(img_bilateral,9,75,75)
    
    plt.subplot(121),plt.imshow(img_bilateral),plt.title('Original')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(blur_bilateral),plt.title('Blurred-Bilateral')
    plt.xticks([]), plt.yticks([])
    plt.suptitle('Bilateral Blurring')
    plt.show()
    
if __name__ == '__main__':
    Convolution2D()
    AveragingBlurring()
    GaussianBlurring()
    MedianBlurring()
    BilateralBlurring()
    