"""
==========================
Object detect.
==========================
Created on June 26, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide ObjDetect for user to detect object related feature in frame of video stream.
@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_objdetect/py_face_detection/py_face_detection.html#face-detection
"""

import copy
import cv2

import Utility as MyUtility

class ObjDetect(object):
    
    '''ObjDetect construction function'''
    def __init__(self):
        #super().__init__()  
        #initialize UserConfig()
        self.userconfig = MyUtility.UserConfig() 
    
    '''detect faces on frame'''    
    def detect_face(self,frame):

        opencv_data = self.userconfig.getOpencvData()+'\haarcascades\haarcascade_frontalface_default.xml'
        
        #face_cascade = cv2.CascadeClassifier('D:\ProgramFiles\opencv\sources\data\haarcascades\haarcascade_frontalface_default.xml')
        face_cascade = cv2.CascadeClassifier(opencv_data)
        
        #copy frame to ret_frame
        ret_frame=copy.deepcopy(frame)
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        #plot rectangle on each face
        for (x,y,w,h) in faces:
            ret_frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)  
        
        #return marked frame and faces list   
        return ret_frame,faces
    
    '''detect eyes on frame'''
    def detect_eye(self,frame):

        opencv_data = self.userconfig.getOpencvData()+'\haarcascades\haarcascade_eye.xml'
        
        #face_cascade = cv2.CascadeClassifier('D:\ProgramFiles\opencv\sources\data\haarcascades\haarcascade_eye.xml')
        eye_cascade = cv2.CascadeClassifier(opencv_data)
        
        #copy frame to ret_frame
        ret_frame=copy.deepcopy(frame)
        
        #get faces list
        tmp_frame, faces = self.detect_face(frame)
        
        
        gray = cv2.cvtColor(ret_frame, cv2.COLOR_BGR2GRAY)
        
        eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)
        
        #for each face to recognize eyes
        for (x,y,w,h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = ret_frame[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
        #plot rectangle on each face
        #for (x,y,w,h) in eyes:
        #    ret_frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)  
              
        return ret_frame
        

def test_fun():
    frame = cv2.imread('../../res/groupface.jpg')
    
    myObjDetect=ObjDetect()
    frame, faces = myObjDetect.detect_face(frame)
    #frame = myObjDetect.detect_eye(frame)
    #print(faces)
    cv2.imshow('Show Image',frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    test_fun()

  
