'''
==========================
Utility
==========================
Created on June 26, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide utility class for user to call function.
'''

import configparser
import cv2
import numpy as np
import math
from enum import Enum

'''
@Function: Manage configuration setting in config.txt file.   
''' 
class UserConfig(object):
    
    def __init__(self):  
        #new a RawConfigParser Objects
        self.myconfig = configparser.RawConfigParser()
        
        #read data from config file
        self.configFilePath = r'Config.txt'

    def getOpencvData(self):
        self.myconfig.read(self.configFilePath)
        _data = self.myconfig.get('Opencv-config', 'opencv_data')
        return _data
    
    def setOpencvData(self,_data):
        self.myconfig.read(self.configFilePath)
        self.myconfig.set('Opencv-config', 'opencv_data', _data)
        self.myconfig.write(open(self.configFilePath, 'w'))

# Define draw type
class DrawType(Enum):
    Default = 0 
    Rect = 1
    Center = 2
    LabelText = 4
    PolyLines = 8

#define Utilities and implement function   
class Utilities():
    ScaleWeight_W=0.15
    ScaleWeight_H=0.2
    
    #return union of r inside q
    @staticmethod
    def union(a,b):
        x = min(a[0], b[0])
        y = min(a[1], b[1])
        w = max(a[0]+a[2], b[0]+b[2]) - x
        h = max(a[1]+a[3], b[1]+b[3]) - y
        return (x, y, w, h)
    
    #return intersection of r and q
    @staticmethod    
    def intersection(a,b):
        x = max(a[0], b[0])
        y = max(a[1], b[1])
        w = min(a[0]+a[2], b[0]+b[2]) - x
        h = min(a[1]+a[3], b[1]+b[3]) - y
        if(w<0 or h<0): 
            return (0,0,0,0)
        return (x, y, w, h)
    
    #return whether contour r inside q
    @staticmethod
    def rectInside(r, q):
        rx, ry, rw, rh = r
        qx, qy, qw, qh = q
        return rx > qx and ry > qy and rx + rw < qx + qw and ry + rh < qy + qh
    
        #get center of r
        '''cen_rx=rx+int(rw/2)
        cen_ry=ry+int(rh/2)
        
        #compare center of r with bound of q to check whether r inside q or not
        return cen_rx > qx and cen_ry > qy and cen_rx < qx + qw and cen_ry < qy + qh'''
   
    #return whether contour r and q overlap beyond overlap rate threshold
    @staticmethod
    def rectOverlap(r, q, _rate=0.5):        
        # intersection: rect1 & rect2
        r_sect = Utilities.intersection(r, q)
        #if r and q has overlap, then check overlap rate
        return Utilities.rectArea(r_sect)>0 and (Utilities.rectArea(r_sect)/Utilities.rectArea(q))>_rate
    
    #return center of rectangle
    @staticmethod
    def rectCenter(r):
        rx, ry, rw, rh = r
    
        #get center of r
        cen_rx=rx + rw/2
        cen_ry=ry + rh/2
        
        #compare center of r with bound of q to check whether r inside q or not
        return cen_rx,cen_ry
   
    #return whether _point inside _rect
    @staticmethod
    def pointInside(_point, _rect):
        px, py = _point
        rx, ry, rw, rh = _rect
        
        #check whether _point is in _rect boundary or not
        pad_w, pad_h = int(Utilities.ScaleWeight_W * rw), int(Utilities.ScaleWeight_H * rh)
        return px > rx-int(pad_w/2) and py > ry-int(pad_h/2) and px < rx + rw+ pad_w and py < ry + rh + pad_h

    
    #return distance of p1 and p2
    @staticmethod
    def pointDistance(_p1, _p2):
        px1, py1 = _p1
        px2, py2 = _p2        
       
        _diff=(px1-px2)**2 + (py1-py2)**2
        
        return np.sqrt(_diff)
    
    #return angle of p1 and p2
    @staticmethod
    def pointAngle(_p1, _p2):
        px1, py1 = _p1
        px2, py2 = _p2        
        
        angle=0        
        x_diff= px2-px1;
        y_diff= py2-py1;
    
        if x_diff==0 and y_diff>0:
            angle = 90
        elif x_diff==0 and y_diff<0:
            angle = 270
        elif y_diff==0 and x_diff>0:
            angle = 360
        elif y_diff==0 and x_diff<0:
            angle = 180
        elif x_diff>0 and y_diff>0:
            angle = math.atan(y_diff/x_diff)*180/math.pi
        elif x_diff<0 and y_diff>0:
            angle = 180 + math.atan(y_diff/x_diff)*180/math.pi
        elif x_diff<0 and y_diff<0:
            angle = 180 + math.atan(y_diff/x_diff)*180/math.pi
        elif x_diff>0 and y_diff<0:
            angle = 360 + math.atan(y_diff/x_diff)*180/math.pi
            
        return angle
    
    #return distance of center of rectangle r1 and p2
    @staticmethod
    def centerRectDistance(_r1, _r2):
        px1, py1 = Utilities.rectCenter(_r1)
        px2, py2 = Utilities.rectCenter(_r2)       
       
        _diff=(px1-px2)**2 + (py1-py2)**2
        
        return np.sqrt(_diff)
    
    #return area of rectangle r
    @staticmethod
    def rectArea(_r):
        _, _, w, h = _r      
        
        _area=int(w*h)
        
        return _area
    
    #return internal radius of rectangle r
    @staticmethod
    def rectRadius(_r):
        _, _, w, h = _r      
        
        _radius=np.sqrt(int(w/2)**2+int(h/2)**2)
        
        return int(_radius)
        
        
    #draw rectangles for found object
    @staticmethod
    def draw_detections(img, rects, _rectColor=(0,0,255), thickness = 1, _mode=DrawType.Default.value):
        for x, y, w, h in rects:
            if(_mode==DrawType.Default.value or 
               _mode&DrawType.Rect.value==DrawType.Rect.value):
                '''=================Drawing Rectangle around bound==================='''
                # the HOG detector returns slightly larger rectangles than the real objects.
                # so we slightly shrink the rectangles to get a nicer output.
                '''pad_w, pad_h = int(Utilities.ScaleWeight_W*w), int(Utilities.ScaleWeight_H*h)
                cv2.rectangle(img, (x-int(pad_w/2), y-int(pad_h/2)), (x+w+pad_w, y+h+pad_h), _rectColor, thickness)'''
                cv2.rectangle(img, (x, y), (x+w, y+h), _rectColor, thickness)
            
            if(_mode==DrawType.Default.value or 
               _mode&DrawType.Center.value==DrawType.Center.value):
                #get center of r
                cen_x, cen_y=Utilities.rectCenter((x, y, w, h))
                '''=================Drawing Circle at center==================='''
                cv2.circle(img,(int(cen_x),int(cen_y)), 3, (0, 0, 255), -1)
    
    #draw label or tracking path for object
    @staticmethod
    def draw_tracking(_frame, _obj, _mode=DrawType.Default.value, thickness = 1):
        x, y, w, h = _obj.rect
        pad_w, pad_h = int(Utilities.ScaleWeight_W*w), int(Utilities.ScaleWeight_H*h)
        if(_mode==DrawType.Default.value or 
           _mode&DrawType.LabelText.value==DrawType.LabelText.value):
            #display object label
            '''x,y=_obj.tracks[-1]
            cv2.putText(_frame, "{}".format(_obj.idx), (int(x-4), int(y-4)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, _obj.color[0].tolist(), 1)'''
            cv2.putText(_frame, "{}".format(_obj.idx), (int(x+pad_w/2), int(y-pad_h/2-5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, _obj.color[0].tolist(), thickness)
        
        if(_mode==DrawType.Default.value or 
           _mode&DrawType.PolyLines.value==DrawType.PolyLines.value):
            #draw moving path
            ls_pts=[]
            for p1, p2 in _obj.tracks:                    
                ls_pts.append([p1,p2])
            pts = np.array([ls_pts], np.int32)
            pts = pts.reshape((-1,1,2))
            cv2.polylines(_frame, [pts], False, _obj.color[0].tolist(), thickness)
        
        if(_mode==DrawType.Default.value or 
           _mode&DrawType.Rect.value==DrawType.Rect.value):
            #draw rectangle
            # the HOG detector returns slightly larger rectangles than the real objects.
            # so we slightly shrink the rectangles to get a nicer output.
            cv2.rectangle(_frame, (x-int(pad_w/2), y-int(pad_h/2)), (x+w+pad_w, y+h+pad_h), _obj.color[0].tolist(), thickness)
        
        if(_mode==DrawType.Default.value or 
           _mode&DrawType.Rect.Center.value==DrawType.Center.value):
            #draw circle over center of tracked object 
            #get center of r
            cen_x, cen_y = _obj.tracks[-1]
            cv2.circle(_frame,(int(cen_x),int(cen_y)), 5, _obj.color[0].tolist(), -1)
        
    #get filtered contours based on _minArea
    @staticmethod
    def cont_filter(cnts, _minArea=25):
        found = []        
        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < _minArea:
                continue
            
            # compute the bounding box for the contour
            found.append(cv2.boundingRect(c))
            
        #return filtered rectangles
        return Utilities.rect_filter(found)
    
    #get filtered rectangle to remove inside ones
    @staticmethod
    def rect_filter(rects):        
        found_filtered = []
        for ri, r in enumerate(rects):
            for qi, q in enumerate(rects):
                if ri != qi and Utilities.rectInside(r, q):
                    break
            found_filtered.append(r)
        return found_filtered
    
    #Show frame and wait user to press q to close window
    @staticmethod
    def Block_Show(_frame):    
        while(True):
            # show the frame and record if the user presses a key
            cv2.imshow("BlockShow", _frame)
            key = cv2.waitKey(1) & 0xFF     
            # if the `q` key is pressed, break from the lop
            if key == ord("q"):
                break
         
        # cleanup the camera and close any open windows
        cv2.destroyWindow('BlockShow')
        #cv2.destroyAllWindows()
    
    #check if point stay in boundary of frame
    @staticmethod
    def pointInBoundary(_frame, _point, _checkmargin=5): 
        #get dim of frame
        height, width, _ = _frame.shape
        
        #get point coordinate
        px, py=_point
        return px > _checkmargin and px < (width-_checkmargin) and py > _checkmargin and py < (height-_checkmargin)
        
        
if __name__ == "__main__":

    userconfig = UserConfig()
    
    print(userconfig.getOpencvData()) 
    #userconfig.setOpencvData("D:\ProgramFiles\opencv\sources\data")
    #print(userconfig.getOpencvData()) 
    p1=(0,0)
    p2=(-1,-2)
    print(Utilities.pointAngle(p1,p2))
    

    