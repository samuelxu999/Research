'''
Created on 2017.07.25

@author: Ronghua Xu        

@Function: Support Vector Machines (SVM)
Learn to use use SVM functionalities in OpenCV

@Reference: http://docs.opencv.org/master/d3/d02/tutorial_py_svm_index.html
'''

import cv2
import numpy as np
import matplotlib.pyplot as plt


SZ=20
bin_n = 16 # Number of bins
affine_flags = cv2.WARP_INVERSE_MAP|cv2.INTER_LINEAR

# takes a digit image and deskew it
def deskew(img):
    m = cv2.moments(img)
    if abs(m['mu02']) < 1e-2:
        return img.copy()
    skew = m['mu11']/m['mu02']
    M = np.float32([[1, skew, -0.5*SZ*skew], [0, 1, 0]])
    img = cv2.warpAffine(img,M,(SZ, SZ),flags=affine_flags)
    return img

#find the HOG Descriptor of each cell.
def hog(img):
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
    mag, ang = cv2.cartToPolar(gx, gy)
    bins = np.int32(bin_n*ang/(2*np.pi))    # quantizing binvalues in (0...16)
    bin_cells = bins[:10,:10], bins[10:,:10], bins[:10,10:], bins[10:,10:]
    mag_cells = mag[:10,:10], mag[10:,:10], mag[:10,10:], mag[10:,10:]
    hists = [np.bincount(b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
    hist = np.hstack(hists)     # hist is a 64 bit vector
    return hist

# apply SVM training and save SVM.dat file
def SVM_Train(srcfile):
        #load image
    img = cv2.imread(srcfile,0)
    if img is None:
        raise Exception("load image data fail!")
        
    # get split image into cells
    cells = [np.hsplit(row,100) for row in np.vsplit(img,50)]
    
    # First half is trainData, remaining is testData
    train_cells = [ i[:50] for i in cells ]
    #test_cells = [ i[50:] for i in cells]
    
    # apply deskew and get hog data 
    deskewed = [list(map(deskew,row)) for row in train_cells]
    hogdata = [list(map(hog,row)) for row in deskewed]
    #print(len(list(hogdata[0])))
    
    #Left image is the original image and right image is the deskewed image.
    plt.subplot(121),plt.imshow(cells[0][0]),plt.title('1) Original'), plt.axis('off')
    plt.subplot(122),plt.imshow(deskewed[0][0]),plt.title('2) Deskewed'), plt.axis('off')
    plt.suptitle('SVM')
    plt.show()
    
    # generate training data and result data
    trainData = np.float32(hogdata).reshape(-1,64)
    responses = np.repeat(np.arange(10),250)[:,np.newaxis]
    
    # create SVM and train data
    svm = cv2.ml.SVM_create()
    svm.setKernel(cv2.ml.SVM_LINEAR)
    svm.setType(cv2.ml.SVM_C_SVC)
    svm.setC(2.67)
    svm.setGamma(5.383)
    svm.train(trainData, cv2.ml.ROW_SAMPLE, responses)
    svm.save('svm_data.dat')

# load svm.dat and execute svm predict over test image
def SVM_Test(imgfile, svmdata):
        #load image
    img = cv2.imread(imgfile,0)
    if img is None:
        raise Exception("Not found SVM data !")
        
    # get split image into cells
    cells = [np.hsplit(row,100) for row in np.vsplit(img,50)]
    
    # First half is trainData, remaining is testData
    test_cells = [ i[50:] for i in cells]
    
    # generate training data and result data
    responses = np.repeat(np.arange(10),250)[:,np.newaxis]
    
    # load SVM data
    svm=cv2.ml.SVM_load(svmdata)
    
    # apply deskew and get hog data
    deskewed = [list(map(deskew,row)) for row in test_cells]
    hogdata = [list(map(hog,row)) for row in deskewed]
    testData = np.float32(hogdata).reshape(-1,bin_n*4)
    
    #get test result
    result = svm.predict(testData)[1]
    mask = result==responses
    correct = np.count_nonzero(mask)
    print(correct*100.0/result.size)
    

if __name__ == '__main__':    
    SVM_Train('../../../res/digits.png')
    SVM_Test('../../../res/digits.png','svm_data.dat')
    