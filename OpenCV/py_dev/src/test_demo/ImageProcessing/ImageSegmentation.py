'''
Created on 2017.07.09

@author: Ronghua Xu        

@Function: Image Segmentation with Watershed Algorithm
We will learn to use marker-based image segmentation using watershed algorithm
We will see: cv2.watershed()

@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_watershed/py_watershed.html
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt
import copy

def Segmation_Watershed():
    
    img = cv2.imread('../../../res/water_coins.jpg')
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    
    # noise removal
    kernel = np.ones((3,3),np.uint8)
    opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
    
    # sure background area
    sure_bg = cv2.dilate(opening,kernel,iterations=3)
    
    # Finding sure foreground area
    dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
    ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)
    
    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)
    
    # Marker labelling
    ret, markers = cv2.connectedComponents(sure_fg)
    
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers+1
    
    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0
    
    markers = cv2.watershed(img,markers)
    img_final=copy.copy(img)
    img_final[markers == -1] = [255,0,0]
    
    plt.subplot(241),plt.imshow(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)),plt.title('1) Original'), plt.axis('off')
    plt.subplot(242),plt.imshow(thresh),plt.title('2) Threshold'), plt.axis('off')
    plt.subplot(243),plt.imshow(opening),plt.title('3) Opening'), plt.axis('off')
    plt.subplot(244),plt.imshow(sure_bg),plt.title('4) Sure background'), plt.axis('off')
    plt.subplot(245),plt.imshow(sure_fg),plt.title('5) Sure foreground'), plt.axis('off')
    plt.subplot(246),plt.imshow(dist_transform),plt.title('6) dist_transform'), plt.axis('off')
    plt.subplot(247),plt.imshow(unknown),plt.title('7) Unknown area'), plt.axis('off')
    plt.subplot(248),plt.imshow(cv2.cvtColor(img_final,cv2.COLOR_BGR2RGB)),plt.title('8) Final'), plt.axis('off')
    plt.suptitle('Watershed Segmation')
    plt.show()

if __name__ == '__main__':
    Segmation_Watershed()