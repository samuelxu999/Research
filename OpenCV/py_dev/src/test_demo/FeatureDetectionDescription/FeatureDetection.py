'''
Created on 2017.06.30

@author: Ronghua Xu        

@Function: Feature Detection and Description

@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_table_of_contents_feature2d/py_table_of_contents_feature2d.html
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt

def HarrisCornerDetection():
    img = cv2.imread('../../../res/chessboard.png')
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

def CornerSubPixelAccuracy():
    img = cv2.imread('../../../res/chessboard.png')
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    # find Harris corners
    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray,2,3,0.04)
    dst = cv2.dilate(dst,None)
    ret, dst = cv2.threshold(dst,0.01*dst.max(),255,0)
    dst = np.uint8(dst)
    
    # find centroids
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)
    
    # define the criteria to stop and refine the corners
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(gray,np.float32(centroids),(5,5),(-1,-1),criteria)
    
    # Now draw them
    res = np.hstack((centroids,corners))
    res = np.int0(res)
    img[res[:,1],res[:,0]]=[0,0,255]
    img[res[:,3],res[:,2]] = [0,255,0]
    
    '''cv2.imshow('Corner SubPixel Accuracy',img)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()'''
    plt.imshow(img),plt.title('Corner SubPixel Accuracy'),plt.show()

def ShiTomasiCornerDetection():  
    img = cv2.imread('../../../res/blox.jpg')
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    corners = cv2.goodFeaturesToTrack(gray,25,0.01,10)
    corners = np.int0(corners)
    
    for i in corners:
        x,y = i.ravel()
        cv2.circle(img,(x,y),3,255,-1)
    
    #plt.imshow(img),plt.title('ShiTomasi Corner Detection'),plt.show()
    cv2.imshow('ShiTomasi Corner Detection',img)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()

def SIFTFeatureDetection():
    img = cv2.imread('../../../res/home.jpg')
    gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    sift = cv2.xfeatures2d.SIFT_create()
    kp = sift.detect(gray,None)
    
    img=cv2.drawKeypoints(gray,kp,None)
    
    #cv2.imwrite('sift_keypoints.jpg',img)
    #plt.imshow(img),plt.title('SIFT Corner Detection'),plt.show()
    cv2.imshow('SIFT Feature Detection',img)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()

def SURFFeatureDetection():
    img = cv2.imread('../../../res/butterfly.jpg',0)
    
    # Create SURF object. You can specify params here or later.
    # Here I set Hessian Threshold to 400
    surf = cv2.xfeatures2d.SURF_create(400)
    
    # Find keypoints and descriptors directly
    kp, des = surf.detectAndCompute(img,None)
    print("kp:%d" %(len(kp)))
    print("surf.hessianThreshold:%f" %(surf.getHessianThreshold()))
    
    # We set it to some 50000. Remember, it is just for representing in picture.
    # In actual cases, it is better to have a value 300-500
    surf.setHessianThreshold(50000)
    
    # Again compute keypoints and check its number.
    kp, des = surf.detectAndCompute(img,None)
    print("kp:%d" %(len(kp)))
    
    #draw it on the image.
    img2 = cv2.drawKeypoints(img,kp,None,(255,0,0),4)
    # Check upright flag, if it False, set it to True
    print("upright flag:%s" %(surf.getUpright()))
    
    # set upright flag
    surf.setUpright(True)
    
    # Recompute the feature points and draw it
    kp = surf.detect(img,None)
    img3 = cv2.drawKeypoints(img,kp,None,(255,0,0),4)

    #plot detect result   
    plt.subplot(121),plt.imshow(img2)
    plt.title('SURF-upright-false'),plt.axis("off")
    plt.subplot(122),plt.imshow(img3)
    plt.title('SURF-upright-true'),plt.axis("off")
    plt.suptitle('SURF Feature Detection')
    plt.show()

def FastCornerDetection():
    img = cv2.imread('../../../res/blox.jpg',0)

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
    plt.suptitle('Fast Feature Detection')
    plt.show()
    
def BRIEF_Detection():
    img = cv2.imread('../../../res/blox.jpg',0)

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
    
    img2 = cv2.drawKeypoints(img, kp, None, color=(255,0,0))
    
    #print(brief.getInt('bytes'))
    #print(brief.__gt__('bytes'))
    print(des.shape)
    
    cv2.imshow('BRIEF_Detection',img2)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()
        
def ORB_Detection():
    img = cv2.imread('../../../res/blox.jpg',0)
    
    # Initiate ORB detector
    orb = cv2.ORB_create()
    
    # find the keypoints with ORB
    kp = orb.detect(img,None)
    
    # compute the descriptors with ORB
    kp, des = orb.compute(img, kp)
    
    # draw only keypoints location,not size and orientation
    img2 = cv2.drawKeypoints(img, kp, None, color=(0,255,0), flags=0)
    
    #plt.imshow(img2), plt.show()
    cv2.imshow('ORB_Detection',img2)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()
    
if __name__ == '__main__':
    HarrisCornerDetection()
    CornerSubPixelAccuracy()
    ShiTomasiCornerDetection()
    SIFTFeatureDetection()
    SURFFeatureDetection()
    FastCornerDetection()
    BRIEF_Detection()
    ORB_Detection()