'''
Created on 2017.07.04

@author: Ronghua Xu        

@Function: Histograms
@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_histograms/py_table_of_contents_histograms/py_table_of_contents_histograms.html
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt

def HistogramsMatplotGray():
    img = cv2.imread('../../../res/home.jpg',0)
    
    #calculate Histogram
    hist = cv2.calcHist([img],[0],None,[256],[0,256])
    
    #Histogram Calculation in Numpy
    #hist,bins = np.histogram(img.ravel(),256,[0,256])
    
    #Plotting Histograms by using matplotlib
    plt.subplot(121),plt.imshow(img,'gray')
    plt.title('Gray'),plt.axis("off")
    plt.subplot(122),plt.hist(img.ravel(),256,[0,256])
    plt.title('Histograms'),plt.xlim([0,256])
    plt.suptitle('Histograms Matplot Gray')
    plt.show()
    
def HistogramsMatplotColor():
    img = cv2.imread('../../../res/home.jpg')
    
    plt.subplot(121),plt.imshow(cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    plt.title('Original'),plt.axis("off")
    plt.subplot(122),plt.title('Histograms'),plt.xlim([0,256])
    color = ('b','g','r')
    for i,col in enumerate(color):
        histr = cv2.calcHist([img],[i],None,[256],[0,256])
        plt.plot(histr,color = col)
    plt.suptitle('Histograms Matplot Color')        
    plt.show()
    
def HistogramsOpencv():
    img = cv2.imread('../../../res/home.jpg',0)
    
    # create a mask
    mask = np.zeros(img.shape[:2], np.uint8)
    mask[100:300, 100:400] = 255
    masked_img = cv2.bitwise_and(img,img,mask = mask)
    
    # Calculate histogram with mask and without mask
    # Check third argument for mask
    hist_full = cv2.calcHist([img],[0],None,[256],[0,256])
    hist_mask = cv2.calcHist([img],[0],mask,[256],[0,256])
    
    #plot result
    plt.subplot(221), plt.title('Original image'), plt.imshow(img, 'gray')
    plt.subplot(222), plt.title('Mask'), plt.imshow(mask,'gray')
    plt.subplot(223), plt.title('Masked image'), plt.imshow(masked_img, 'gray')
    plt.subplot(224), plt.title('Histograms'), plt.plot(hist_full), plt.plot(hist_mask), plt.xlim([0,256])
    plt.suptitle('Histograms Opencv')
    plt.show()

if __name__ == '__main__':
    HistogramsMatplotGray()
    HistogramsMatplotColor()
    HistogramsOpencv()
    