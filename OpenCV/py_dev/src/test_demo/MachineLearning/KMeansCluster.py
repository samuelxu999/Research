'''
Created on 2017.07.25

@author: Ronghua Xu        

@Function: K-Means Clustering 
Learn to use cv2.kmeans() function in OpenCV for data clustering

@Reference: http://docs.opencv.org/master/d9/d70/tutorial_py_kmeans_index.html
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt

def OneFeature():
    # generate test data
    x = np.random.randint(25,100,25)
    y = np.random.randint(175,255,25)
    z = np.hstack((x,y))
    z = z.reshape((50,1))
    z = np.float32(z)
    
    # Define criteria = ( type, max_iter = 10 , epsilon = 1.0 )
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    
    # Set flags (Just to avoid line break in the code)
    flags = cv2.KMEANS_RANDOM_CENTERS
    
    # Apply KMeans
    compactness,labels,centers = cv2.kmeans(z,2,None,criteria,10,flags)
    
    A = z[labels==0]
    B = z[labels==1]
    
    # Now plot 'A' in red, 'B' in blue, 'centers' in yellow
    plt.hist(A,256,[0,256],color = 'r')
    plt.hist(B,256,[0,256],color = 'b')
    plt.hist(centers,32,[0,256],color = 'y')   
    plt.title('One Feature'), plt.show()
    
def MultiFeature():
    # generate test data
    X = np.random.randint(25,50,(25,2))
    Y = np.random.randint(60,85,(25,2))
    Z = np.vstack((X,Y))
    
    # convert to np.float32
    Z = np.float32(Z)
    # define criteria and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret,label,center=cv2.kmeans(Z,2,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
    # Now separate the data, Note the flatten()
    A = Z[label.ravel()==0]
    B = Z[label.ravel()==1]
    # Plot the data
    plt.scatter(A[:,0],A[:,1])
    plt.scatter(B[:,0],B[:,1],c = 'r')
    plt.scatter(center[:,0],center[:,1],s = 80,c = 'y', marker = 's')
    plt.xlabel('Height'),plt.ylabel('Weight')
    plt.title('Multiple Feature'),plt.show()
    
def ColorQuantization():
    img = cv2.imread('../../../res/home.jpg')
    Z = img.reshape((-1,3))
    
    # convert to np.float32
    Z = np.float32(Z)
    
    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    
    # test when K=2
    K = 2
    ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
    
    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((img.shape))
    
    # test when K=4
    K = 4
    ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
    
    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res4 = res.reshape((img.shape))
    
    # test when K=8
    K = 8
    ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
    
    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res8 = res.reshape((img.shape))
    
    #display result
    plt.subplot(221),plt.imshow(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)),plt.title('1) Original'), plt.axis('off')
    plt.subplot(222),plt.imshow(cv2.cvtColor(res2,cv2.COLOR_BGR2RGB)),plt.title('2) K=2'), plt.axis('off')
    plt.subplot(223),plt.imshow(cv2.cvtColor(res4,cv2.COLOR_BGR2RGB)),plt.title('2) K=4'), plt.axis('off')
    plt.subplot(224),plt.imshow(cv2.cvtColor(res8,cv2.COLOR_BGR2RGB)),plt.title('2) K=8'), plt.axis('off')
    plt.suptitle('Color Quantization')
    plt.show()

if __name__ == '__main__':
    OneFeature()
    MultiFeature()
    ColorQuantization()
    