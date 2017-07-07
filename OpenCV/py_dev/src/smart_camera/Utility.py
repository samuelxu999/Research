"""
==========================
Utility
==========================
Created on June 26, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide utility class for user to call function.
"""

import configparser
import cv2

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

class Utilities():
    #return whether contour r inside q
    @staticmethod
    def inside(r, q):
        rx, ry, rw, rh = r
        qx, qy, qw, qh = q
        return rx > qx and ry > qy and rx + rw < qx + qw and ry + rh < qy + qh
    
    #draw rectangles for found object
    @staticmethod
    def draw_detections(img, rects, thickness = 1):
        for x, y, w, h in rects:
            # the HOG detector returns slightly larger rectangles than the real objects.
            # so we slightly shrink the rectangles to get a nicer output.
            pad_w, pad_h = int(0.15*w), int(0.05*h)
            cv2.rectangle(img, (x+pad_w, y+pad_h), (x+w-pad_w, y+h-pad_h), (0, 255, 0), thickness)
    
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
                if ri != qi and Utilities.inside(r, q):
                    break
            else:
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

if __name__ == "__main__":

    userconfig = UserConfig()
    
    print(userconfig.getOpencvData()) 
    #userconfig.setOpencvData("D:\ProgramFiles\opencv\sources\data")
    #print(userconfig.getOpencvData()) 
    

    