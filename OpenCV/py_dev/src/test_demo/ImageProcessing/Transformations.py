'''
Created on 2017.07.03

@author: Ronghua Xu        

@Function: Geometric Transformations of Images
Learn to apply different geometric transformation to images like translation, rotation, affine transformation etc.
You will see these functions: cv2.getPerspectiveTransform

@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_geometric_transformations/py_geometric_transformations.html
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt

#Scaling is just resizing of the image.
def Scaling(mode=True):
    img = cv2.imread('../../../res/messi5.jpg')
    
    if(mode):
        res = cv2.resize(img,None,fx=2, fy=2, interpolation = cv2.INTER_CUBIC)
    
    else:
        height, width = img.shape[:2]
        res = cv2.resize(img,(int(width/2), int(height/2)), interpolation = cv2.INTER_CUBIC)

    cv2.imshow('Scaling',res)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#Translation is the shifting of object's location
def Translation():
    img = cv2.imread('../../../res/messi5.jpg',0)
    rows,cols = img.shape
    
    M = np.float32([[1,0,100],[0,1,50]])
    dst = cv2.warpAffine(img,M,(cols,rows))
    
    cv2.imshow('Translation',dst)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#Rotation is the rotate image based on angle
def Rotation():
    img = cv2.imread('../../../res/messi5.jpg',0)
    rows,cols = img.shape
    
    M = cv2.getRotationMatrix2D((cols/2,rows/2),90,1)
    dst = cv2.warpAffine(img,M,(cols,rows))
    
    cv2.imshow('Rotation',dst)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#Affine Transformation   
def Affine():
    img = cv2.imread('../../../res/drawing.jpg')
    rows,cols,ch = img.shape
    
    pts1 = np.float32([[50,50],[200,50],[50,200]])
    pts2 = np.float32([[10,100],[200,50],[100,250]])
    
    M = cv2.getAffineTransform(pts1,pts2)
    
    dst = cv2.warpAffine(img,M,(cols,rows))
    
    plt.subplot(121),plt.imshow(img),plt.title('Input')
    plt.subplot(122),plt.imshow(dst),plt.title('Output')
    plt.show()

#Perspective Transformation    
def Perspective():
    img = cv2.imread('../../../res/sudoku.png')
    rows,cols,ch = img.shape
    
    pts1 = np.float32([[56,65],[368,52],[28,387],[389,390]])
    pts2 = np.float32([[0,0],[300,0],[0,300],[300,300]])
    
    M = cv2.getPerspectiveTransform(pts1,pts2)
    
    dst = cv2.warpPerspective(img,M,(300,300))
    
    plt.subplot(121),plt.imshow(img),plt.title('Input')
    plt.subplot(122),plt.imshow(dst),plt.title('Output')
    plt.show()
    

if __name__ == '__main__':
    Scaling(False)
    Translation()
    Rotation()
    Affine()
    Perspective()
    