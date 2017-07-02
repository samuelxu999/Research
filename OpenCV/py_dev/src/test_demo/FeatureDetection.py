'''
Created on 2017.06.30

@author: Ronghua Xu        
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt

'''
@Function: Feature Detection and Description
@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_table_of_contents_feature2d/py_table_of_contents_feature2d.html
'''

def HarrisCornerDetection():
    img = cv2.imread('../../res/chessboard.png')
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray,2,3,0.04)
    
    #result is dilated for marking the corners, not important
    dst = cv2.dilate(dst,None)
    
    # Threshold for an optimal value, it may vary depending on the image.
    img[dst>0.01*dst.max()]=[0,0,255]
    
    cv2.imshow('HarrisCornerDetection',img)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()

def ShiTomasiCornerDetection():  
    img = cv2.imread('../../res/blox.jpg')
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    corners = cv2.goodFeaturesToTrack(gray,25,0.01,10)
    corners = np.int0(corners)
    
    for i in corners:
        x,y = i.ravel()
        cv2.circle(img,(x,y),3,255,-1)
    
    plt.imshow(img),plt.show()

def FastCornerDetection():
    img = cv2.imread('../../res/blox.jpg',0)

    # Initiate FAST object with default values
    fast = cv2.FastFeatureDetector_create()
    
    # find and draw the keypoints
    kp = fast.detect(img,None)
    img2 = cv2.drawKeypoints(img, kp, None, color=(255,0,0))
    
    # Print all default params
    print("Threshold: ", fast.getThreshold())
    print("nonmaxSuppression: ", fast.getNonmaxSuppression())
    print("neighborhood: ", fast.getType())
    print("Total Keypoints with nonmaxSuppression: ", len(kp))
    
    # Disable nonmaxSuppression
    fast.setNonmaxSuppression(False)
    kp = fast.detect(img,None)
    
    print("Total Keypoints without nonmaxSuppression: ", len(kp))
    
    img3 = cv2.drawKeypoints(img, kp, None, color=(255,0,0))
    
    #plot detect result    
    plt.subplot(121),plt.imshow(img2),plt.title('fast_true')
    plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(img3),plt.title('fast_false')
    plt.xticks([]), plt.yticks([])
    plt.show()
    
def BRIEF_Detection():
    img = cv2.imread('../../res/blox.jpg',0)

    # Initiate STAR detector
    #star = cv2.FeatureDetector_create("STAR")
    star = cv2.xfeatures2d.StarDetector_create()

    # Initiate BRIEF extractor
    #brief = cv2.DescriptorExtractor_create("BRIEF")
    brief = cv2.xfeatures2d.BriefDescriptorExtractor_create()
    
    # find the keypoints with STAR
    kp = star.detect(img,None)
    
    # compute the descriptors with BRIEF
    kp, des = brief.compute(img, kp)
    
    #print(brief.getInt('bytes'))
    #print(brief.__gt__('bytes'))
    print(des.shape)
    
if __name__ == '__main__':
    #HarrisCornerDetection()
    #ShiTomasiCornerDetection()
    #FastCornerDetection()
    BRIEF_Detection()
    