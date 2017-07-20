'''
==========================
Object detect.
==========================
Created on June 26, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide ObjDetect for user to detect object related feature in frame of video stream.
@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_objdetect/py_face_detection/py_face_detection.html#face-detection
'''

import numpy as np
import copy
import cv2
from enum import Enum
import Utility as MyUtility

# Define feature type
class FeatureTpye(Enum):
    NoFeature = 0 
    Face = 1
    Eyes = 2
    Body = 3

# Define motion type:Static--Compared with background frame;Dynamic--compare between pre_frame and cur_frame
class MotionType(Enum):
    Static = 0
    Dynamic = 1
    
#define MotionMethod 
class MotionMethod(Enum):
    Diff = 0 
    MOG = 1 
    MOG2 = 2

class ObjDetect(object):
    
    '''ObjDetect construction function'''
    def __init__(self):
        #super().__init__()  
        #initialize UserConfig()
        self.userconfig = MyUtility.UserConfig()
        #initialize BackgroundSubtractorMOG
        self.bgSubMOG = cv2.bgsegm.createBackgroundSubtractorMOG()
        self.bgSubMOG2 = cv2.createBackgroundSubtractorMOG2(detectShadows = True)
    
    '''detect faces on frame'''    
    def detect_face(self,frame):

        opencv_data = self.userconfig.getOpencvData()+'/haarcascades/haarcascade_frontalface_alt.xml'
        
        #opencv_data = self.userconfig.getOpencvData()+'/haarcascades/haarcascade_upperbody.xml'
        
        #face_cascade = cv2.CascadeClassifier('D:\ProgramFiles/opencv/sources/data/haarcascades/haarcascade_frontalface_default.xml')
        face_cascade = cv2.CascadeClassifier(opencv_data)
        
        #copy frame to ret_frame
        ret_frame=copy.deepcopy(frame)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        #plot rectangle on each face
        '''for (x,y,w,h) in faces:
            ret_frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)  '''
        
        #used for filtered found object to only record father contour's location        
        #found_filtered=MyUtility.Utilities.rect_filter(faces)
        
        #return marked frame and faces list   
        return ret_frame,faces
    
    '''detect eyes on frame'''
    def detect_eye(self,frame):

        opencv_data = self.userconfig.getOpencvData()+'/haarcascades/haarcascade_eye.xml'
        
        #face_cascade = cv2.CascadeClassifier('D:\ProgramFiles/opencv/sources/data/haarcascades/haarcascade_eye.xml')
        eye_cascade = cv2.CascadeClassifier(opencv_data)
        
        #copy frame to ret_frame
        ret_frame=copy.deepcopy(frame)
        
        #get faces list
        _, faces = self.detect_face(frame)        
        
        gray = cv2.cvtColor(ret_frame, cv2.COLOR_BGR2GRAY)
        
        eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)
        
        #for each face to recognize eyes
        for (x,y,w,h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = ret_frame[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
              
        return ret_frame
       
    def detectBody(self, _frame):
        #new HOGDescriptor and set DefaultPeopleDetector
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector( cv2.HOGDescriptor_getDefaultPeopleDetector() ) 
        
        #get hog.detectMultiScale() result: location and weight
        found, _ = hog.detectMultiScale(_frame, winStride=(8,8), padding=(32,32), scale=1.05)
        
        #used for filtered found object to only record father contour's location        
        found_filtered=MyUtility.Utilities.rect_filter(found)
        
        return found_filtered
    
    '''
    Compare difference between _preframe and _curframe to detect object
    '''    
    def detectMotionDiff(self,_preframe,_curframe,_minArea,_mode=MotionType.Static):
        # resize the frame, convert it to grayscale, and blur it
        gray = cv2.cvtColor(_curframe, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # compute the absolute difference between the current frame and first frame
        frameDelta = cv2.absdiff(_preframe, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        
        #refresh _preframe
        if(_mode==MotionType.Dynamic):
                _preframe=copy.copy(gray)

        # dilate the thresholded image to fill in holes, then find contours on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        #MyUtility.Utilities.Block_Show(thresh)
        
        _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        #get filtered contour rectangles
        found_filtered=MyUtility.Utilities.cont_filter(cnts, _minArea)
      
        return _preframe, found_filtered
    
    '''
    Through BackgroundSubtractorMOG
    ''' 
    def detectMotionMOG(self,_frame, _minArea, _mode=MotionMethod.MOG2):
        
        # Blur Filtering
        blur= cv2.medianBlur(_frame,5)
        #blur = cv2.GaussianBlur(_frame,(5,5),0)
        #blur = cv2.bilateralFilter(_frame,9,75,75)
        
        #get background mask
        if(_mode==MotionMethod.MOG):
            fgmask = self.bgSubMOG.apply(blur)
        elif(_mode==MotionMethod.MOG2):
            fgmask = self.bgSubMOG2.apply(blur)
        else:
            return 0
        
        
        #threshold to remove shadow
        _,fgmask = cv2.threshold(fgmask,127,255,cv2.THRESH_BINARY)
        
        # noise removal
        kernel = np.ones((2,2),np.uint8)
        fgmask = cv2.erode(fgmask,kernel,iterations = 1)
        fgmask = cv2.morphologyEx(fgmask,cv2.MORPH_OPEN,kernel,iterations = 1)
        fgmask = cv2.morphologyEx(fgmask,cv2.MORPH_CLOSE,kernel,iterations = 1)
        fgmask = cv2.dilate(fgmask,kernel,iterations = 1)
        
        #MyUtility.Utilities.Block_Show(fgmask)
        
        # find contours on thresholded image
        _, cnts, _ = cv2.findContours(fgmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        #get filtered contour rectangles
        found_filtered=MyUtility.Utilities.cont_filter(cnts, _minArea)
            
        return found_filtered   

def test_fun():
    frame = cv2.imread('../../res/groupface.jpg')
    #frame = cv2.imread('../../res/kobe.bmp')
    
    myObjDetect=ObjDetect()
    frame, faces = myObjDetect.detect_face(frame)
    #frame = myObjDetect.detect_eye(frame)
    #myObjDetect.detectBody(frame)
    cv2.imshow('Show Image',frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_fun()

  
