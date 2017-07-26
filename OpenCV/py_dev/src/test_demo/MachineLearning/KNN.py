'''
Created on 2017.07.25

@author: Ronghua Xu        

@Function: K-Nearest Neighbour
Learn to use kNN for classification Plus learn about handwritten digit recognition using kNN

@Reference: http://docs.opencv.org/master/d0/d72/tutorial_py_knn_index.html
'''

import cv2
import numpy as np
import matplotlib.pyplot as plt

def KNN_Basic():
    ''' We create 25 families or 25 training data, and label them either Class-0 or Class-1. '''
    # Feature set containing (x,y) values of 25 known/training data
    trainData = np.random.randint(0,100,(25,2)).astype(np.float32)
    
    # Labels each one either Red or Blue with numbers 0 and 1
    responses = np.random.randint(0,2,(25,1)).astype(np.float32)
    
    # Take Red families and plot them
    red = trainData[responses.ravel()==0]
    plt.scatter(red[:,0],red[:,1],80,'r','^')
    
    # Take Blue families and plot them
    blue = trainData[responses.ravel()==1]
    plt.scatter(blue[:,0],blue[:,1],80,'b','s')
    
    ''' Bring one new-comer and classify him to a family with the help of kNN in OpenCV. '''
    newcomer = np.random.randint(0,100,(1,2)).astype(np.float32)
    plt.scatter(newcomer[:,0],newcomer[:,1],80,'g','o')
    
    ''' Next initiate the kNN algorithm and pass the trainData and responses to train the kNN (It constructs a search tree). '''
    knn = cv2.ml.KNearest_create()
    knn.train(trainData, cv2.ml.ROW_SAMPLE, responses)
    ret, results, neighbours ,dist = knn.findNearest(newcomer, 3)
    
    ''' Print out test result '''
    print( "result:  {}\n".format(results) )
    print( "neighbours:  {}\n".format(neighbours) )
    print( "distance:  {}\n".format(dist) )
    
    plt.show()
    
def OCR_Digit():
    ''' Read handwritten digits and train them'''
    # Read handwritten digits image
    img = cv2.imread('../../../res/digits.png')
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    
    # Now we split the image to 5000 cells, each 20x20 size
    cells = [np.hsplit(row,100) for row in np.vsplit(gray,50)]
    
    # Make it into a Numpy array. It size will be (50,100,20,20)
    x = np.array(cells)
    
    # Now we prepare train_data and test_data.
    train = x[:,:50].reshape(-1,400).astype(np.float32) # Size = (2500,400)
    test = x[:,50:100].reshape(-1,400).astype(np.float32) # Size = (2500,400)
    
    # Create labels for train and test data
    k = np.arange(10)
    train_labels = np.repeat(k,250)[:,np.newaxis]
    test_labels = train_labels.copy()
    
    # Initiate kNN, train the data, then test it with test data for k=1
    knn = cv2.ml.KNearest_create()
    knn.train(train, cv2.ml.ROW_SAMPLE, train_labels)
    ret,result,neighbours,dist = knn.findNearest(test,k=5)
    
    # Now we check the accuracy of classification
    # For that, compare the result with test_labels and check which are wrong
    matches = result==test_labels
    correct = np.count_nonzero(matches)
    accuracy = correct*100.0/result.size    
    print( accuracy )
    
    # save the data
    np.savez('knn_data.npz',train=train, train_labels=train_labels)
 
def OCR_LoadData(datafile):  
    # Now load the data
    with np.load(datafile) as data:
        print( data.files )
        train = data['train']
        train_labels = data['train_labels']
    print(train[0])
    print(train_labels[0])

def OCR_Alphabets():
    # Load the data, converters convert the letter to a number
    data= np.loadtxt('../../../res/letter-recognition.data', dtype= 'float32', delimiter = ',',
                        converters= {0: lambda ch: ord(ch)-ord('A')})
    # split the data to two, 10000 each for train and test
    train, test = np.vsplit(data,2)
    # split trainData and testData to features and responses
    responses, trainData = np.hsplit(train,[1])
    train_labels, testData = np.hsplit(test,[1])
    # Initiate the kNN, classify, measure accuracy.
    knn = cv2.ml.KNearest_create()
    knn.train(trainData, cv2.ml.ROW_SAMPLE, responses)
    ret, result, neighbours, dist = knn.findNearest(testData, k=5)
    
    correct = np.count_nonzero(result == train_labels)
    accuracy = correct*100.0/10000
    print( accuracy )    
    
    # save the data
    np.savez('knn_data.npz',train=train, train_labels=train_labels)   
    
if __name__ == '__main__':
    #KNN_Basic()
    OCR_Digit()
    #OCR_Alphabets()
    OCR_LoadData('knn_data.npz')