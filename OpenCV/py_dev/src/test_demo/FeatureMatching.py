'''
Created on 2017.06.30

@author: Ronghua Xu        
'''

import cv2
from matplotlib import pyplot as plt

'''
@Function: Feature Matching
We will see how to match features in one image with others
We will use the Brute-Force matcher and FLANN Matcher in OpenCV
@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_matcher/py_matcher.html#matcher
'''

def Basic_BFMatcher():
    img1 = cv2.imread('../../res/box_in.png',0)          # queryImage
    img2 = cv2.imread('../../res/box_in_scene.png',0)    # trainImage
    
    # Initiate SIFT detector
    orb = cv2.ORB_create()
    
    # find the keypoints and descriptors with SIFT
    kp1, des1 = orb.detectAndCompute(img1,None)
    kp2, des2 = orb.detectAndCompute(img2,None)
    
    # create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    # Match descriptors.
    matches = bf.match(des1,des2)
    
    # Sort them in the order of their distance.
    matches = sorted(matches, key = lambda x:x.distance)
    
    # Draw first 10 matches.
    img3 = cv2.drawMatches(img1,kp1,img2,kp2,matches[:10], None, flags=2)
    
    plt.imshow(img3)
    plt.show()

if __name__ == '__main__':
    Basic_BFMatcher()
    