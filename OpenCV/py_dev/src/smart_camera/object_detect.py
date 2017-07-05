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
    
    #return whether contour r inside q
    def inside(self, r, q):
        rx, ry, rw, rh = r
        qx, qy, qw, qh = q
        return rx > qx and ry > qy and rx + rw < qx + qw and ry + rh < qy + qh
    
    #draw rectangles for found object
    def draw_detections(self, img, rects, thickness = 1):
        for x, y, w, h in rects:
            # the HOG detector returns slightly larger rectangles than the real objects.
            # so we slightly shrink the rectangles to get a nicer output.
            pad_w, pad_h = int(0.15*w), int(0.05*h)
            cv2.rectangle(img, (x+pad_w, y+pad_h), (x+w-pad_w, y+h-pad_h), (0, 255, 0), thickness)

    def detectBody(self, _frame):
        #new HOGDescriptor and set DefaultPeopleDetector
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector( cv2.HOGDescriptor_getDefaultPeopleDetector() ) 
        
        #get hog.detectMultiScale() result
        found, w = hog.detectMultiScale(_frame, winStride=(8,8), padding=(32,32), scale=1.05)
        
        #used for filtered found object to only record maximum rectangles
        found_filtered = []        
        for ri, r in enumerate(found):
            for qi, q in enumerate(found):
                if ri != qi and self.inside(r, q):
                    break
            else:
                found_filtered.append(r)
        
        #self.draw_detections(_frame, found)
        self.draw_detections(_frame, found_filtered, 1)
        
    def detectMotion(self,_firstframe,_frame,_minArea):
        # resize the frame, convert it to grayscale, and blur it
        gray = cv2.cvtColor(_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # compute the absolute difference between the current frame and first frame
        frameDelta = cv2.absdiff(_firstframe, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        
        # dilate the thresholded image to fill in holes, then find contours on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        tmp_img, cnts, _temp = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        text="Free"
        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < _minArea:
                continue
     
            # compute the bounding box for the contour, draw it on the frame,
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Occupied"
            
        # draw the text and timestamp on the frame
        cv2.putText(_frame, "Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

def test_fun():
    frame = cv2.imread('../../res/groupface.jpg')
    
    myObjDetect=ObjDetect()
    #frame, faces = myObjDetect.detect_face(frame)
    #frame = myObjDetect.detect_eye(frame)
    myObjDetect.detectBody(frame)
    cv2.imshow('Show Image',frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    test_fun()

  
