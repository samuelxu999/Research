'''
Created on 2017.07.04

@author: Ronghua Xu        

@Function: Image Pyramids
We will learn about Image Pyramids
We will use Image pyramids to create a new fruit, "Orapple"
We will see these functions: cv2.pyrUp(), cv2.pyrDown()

@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_pyramids/py_pyramids.html
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt

# test basic function of cv2.pyrUp(), cv2.pyrDown()
def Theory_test():
    img = cv2.imread('../../../res/messi5.jpg')
    higher_reso = cv2.pyrUp(img)
    lower_reso=cv2.pyrDown(img)
    higher_reso2 = cv2.pyrUp(lower_reso)
    
    #display result
    plt.subplot(2,2,1),plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title('Original'), plt.axis("off")
    plt.subplot(2,2,2),plt.imshow(cv2.cvtColor(higher_reso, cv2.COLOR_BGR2RGB))
    plt.title('higher_reso'), plt.axis("off")
    plt.subplot(2,2,3),plt.imshow(cv2.cvtColor(lower_reso, cv2.COLOR_BGR2RGB))
    plt.title('lower_reso'), plt.axis("off")
    plt.subplot(2,2,4),plt.imshow(cv2.cvtColor(higher_reso2, cv2.COLOR_BGR2RGB))
    plt.title('higher_reso2'), plt.axis("off")
    plt.suptitle('Image Pyramid Theory Test')
    plt.show()
 
'''
1. Load the two images of apple and orange
2. Find the Gaussian Pyramids for apple and orange (in this particular example, number of levels is 6)
3. From Gaussian Pyramids, find their Laplacian Pyramids
4. Now join the left half of apple and right half of orange in each levels of Laplacian Pyramids
5. Finally from this joint image pyramids, reconstruct the original image.
'''    
def ImageBlending():
    A = cv2.imread('../../../res/apple.jpg')
    B = cv2.imread('../../../res/orange.jpg')
    
    # generate Gaussian pyramid for A
    G = A.copy()
    gpA = [G]
    for i in range(6):
        G = cv2.pyrDown(G)
        gpA.append(G)
    
    # generate Gaussian pyramid for B
    G = B.copy()
    gpB = [G]
    for i in range(6):
        G = cv2.pyrDown(G)
        gpB.append(G)
    
    # generate Laplacian Pyramid for A
    lpA = [gpA[5]]
    for i in range(5,0,-1):
        GE = cv2.pyrUp(gpA[i])
        L = cv2.subtract(gpA[i-1],GE)
        lpA.append(L)
    
    # generate Laplacian Pyramid for B
    lpB = [gpB[5]]
    for i in range(5,0,-1):
        GE = cv2.pyrUp(gpB[i])
        L = cv2.subtract(gpB[i-1],GE)
        lpB.append(L)
    
    # Now add left and right halves of images in each level
    LS = []
    for la,lb in zip(lpA,lpB):
        rows,cols,dpt = la.shape
        ls = np.hstack((la[:,0:int(cols/2)], lb[:,int(cols/2):]))
        LS.append(ls)
    
    # now reconstruct
    ls_ = LS[0]
    for i in range(1,6):
        ls_ = cv2.pyrUp(ls_)
        ls_ = cv2.add(ls_, LS[i])
    
    # image with direct connecting each half
    real = np.hstack((A[:,:int(cols/2)],B[:,int(cols/2):]))

    #display result   
    plt.subplot(2,2,1),plt.imshow(cv2.cvtColor(A, cv2.COLOR_BGR2RGB))
    plt.title('Apple'), plt.axis("off")
    plt.subplot(2,2,2),plt.imshow(cv2.cvtColor(B, cv2.COLOR_BGR2RGB))
    plt.title('Orange'), plt.axis("off")
    plt.subplot(2,2,3),plt.imshow(cv2.cvtColor(real, cv2.COLOR_BGR2RGB))
    plt.title('Direct Connection'), plt.axis("off")
    plt.subplot(2,2,4),plt.imshow(cv2.cvtColor(ls_, cv2.COLOR_BGR2RGB))
    plt.title('Pyramid Blending'), plt.axis("off")
    plt.suptitle('Image Pyramid Blending Test')
    plt.show()

if __name__ == '__main__':
    Theory_test()
    ImageBlending()
    