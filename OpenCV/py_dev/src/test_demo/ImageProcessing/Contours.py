'''
Created on 2017.06.28

@author: Ronghua Xu        

@Function: Contours in OpenCV

@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_contours/py_table_of_contents_contours/py_table_of_contents_contours.html
'''

import numpy as np
import cv2
from matplotlib import pyplot as plt
import copy

'''
Get contours in image
@defaultmode: Contour Approximation Method:
                --cv2.CHAIN_APPROX_SIMPLE:True
                --cv2.CHAIN_APPROX_NONE:False
@contours: return contours array
'''
def GetContours(_img, defaultmode=True):
    imgray = cv2.cvtColor(_img,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,127,255,0)
    if(defaultmode):
        image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    else:        
        image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

    return contours

'''
Find contours in image
@contours: input contours array
@defaultmode: Draw contour Method:
                --To draw all contours: True
                --To draw an individual contour:False
'''
def DrawContours(contours, defaultmode=True):
    # Create a black image
    img = np.zeros((255,255,3), np.uint8)
    
    if(defaultmode):
        # To draw all contours, pass -1) and remaining arguments are color, thickness etc.
        img = cv2.drawContours(img, contours, -1, (0,255,0), 3)
    else:
        #To draw an individual contour
        cnt = contours[0]
        for i in range(len(cnt)):
            img = cv2.drawContours(img, cnt, i, (0,255,0), 3)
    
    #Show image
    cv2.namedWindow("Draw Contours")   
    cv2.imshow("Draw Contours", img)   
    cv2.waitKey (0)  
    cv2.destroyAllWindows()

'''
Get moments in contours
@contours: input contours array
@_momoent: return moment
'''   
def GetMoments(contours):    
    _cnt = contours[0]
    _momoent = cv2.moments(_cnt)
    #print(_momoent)
    return _momoent

'''
Get Contour Area
@contours: input contours array
@_area: return moment
'''   
def GetContourArea(contours):    
    _cnt = contours[0]
    _area = cv2.contourArea(_cnt)
    #print(_momoent)
    return _area

'''
Get Contour Perimeter
@contours: input contours array
@_perimeter: return moment
'''   
def GetContourPerimeter(contours):    
    _cnt = contours[0]
    #closed contour (if passed True), or just a curve
    _perimeter  = cv2.arcLength(_cnt,True)
    #print(_momoent)
    return _perimeter

def test_contours():
    #cnt=GetContours('../../res/box.jpg')
    img=cv2.imread('../../../res/thunder.jpg')
    cnt=GetContours(img)
    print("Contours number are:%d" %(len(cnt[0])))
    print("Moments:%s" %(GetMoments(cnt)))
    print("Contour Area:%s" %(GetContourArea(cnt)))
    print("Contour Perimeter:%s" %(GetContourPerimeter(cnt)))
    DrawContours(cnt,False)

def BoundingRectangle():
    img = cv2.imread('../../../res/thunder.jpg')
    cnt=GetContours(img)    

    #Straight Bounding Rectangle
    img1=copy.deepcopy(img)
    x,y,w,h = cv2.boundingRect(cnt[0])
    img1 = cv2.rectangle(img1,(x,y),(x+w,y+h),(0,255,0),2)
    
    #Rotated Rectangle
    img2=copy.deepcopy(img)
    rect = cv2.minAreaRect(cnt[0])
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    img2 = cv2.drawContours(img2,[box],0,(0,0,255),2)
    
    #Minimum Enclosing Circle
    img3=copy.deepcopy(img)
    (x,y),radius = cv2.minEnclosingCircle(cnt[0])
    center = (int(x),int(y))
    radius = int(radius)
    img3 = cv2.circle(img3,center,radius,(255,0,0),2)
    
    #Fitting an Ellipse
    img4=copy.deepcopy(img)
    ellipse = cv2.fitEllipse(cnt[0])
    img4 = cv2.ellipse(img4,ellipse,(255,255,0),2)
    
    #Fitting a Line
    img5=copy.deepcopy(img)
    rows,cols = img.shape[:2]
    [vx,vy,x,y] = cv2.fitLine(cnt[0], cv2.DIST_L2,0,0.01,0.01)
    lefty = int((-x*vy/vx) + y)
    righty = int(((cols-x)*vy/vx)+y)
    img5 = cv2.line(img5,(cols-1,righty),(0,lefty),(0,255,255),2)
    
    #Show image    
    titles = ['Original Image', 'Straight Bounding Rectangle',
            'Rotated Rectangle', 'Minimum Enclosing Circle',
            'Fitting an Ellipse', 'Fitting a Line']
    
    images = [img, img1, img2, img3, img4, img5]
    
    for i in range(6):
        plt.subplot(3,2,i+1),plt.imshow(images[i],'gray')
        plt.title(titles[i])
        plt.xticks([]),plt.yticks([])
    plt.suptitle('Bounding Rectangle Test')
    plt.show()
    
def ConvexityDefects():
    #load image
    img = cv2.imread('../../../res/star.jpg')
    
    #get contours
    contours=GetContours(img)    
    cnt = contours[0]
    
    hull = cv2.convexHull(cnt,returnPoints = False)
    defects = cv2.convexityDefects(cnt,hull)
    
    for i in range(defects.shape[0]):
        s,e,f,d = defects[i,0]
        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])
        cv2.line(img,start,end,[0,255,0],2)
        cv2.circle(img,far,5,[0,0,255],-1)
    
    cv2.imshow('Convexity Defects',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
'''
cv2.matchShapes():compare two shapes, or two contours and returns a metric showing the similarity.
'''    
def MatchShapes():
    img1 = cv2.imread('../../../res/star.jpg')
    img2 = cv2.imread('../../../res/star2.jpg')
    
    #get contours
    contours1=GetContours(img1) 
    cnt1 = contours1[0]
    contours2=GetContours(img2) 
    cnt2 = contours2[0]
    
    ret = cv2.matchShapes(cnt1,cnt2,1,0.0)
    print("Match shape:%f" %(ret))

if __name__ == '__main__':
    test_contours()
    BoundingRectangle()
    ConvexityDefects()
    MatchShapes()
    