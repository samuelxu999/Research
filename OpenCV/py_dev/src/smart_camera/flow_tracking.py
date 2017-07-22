'''
==========================
Flow trackiong.
==========================
Created on July 10, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide moving object tracking by processing frame of video stream.
@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_video/py_lucas_kanade/py_lucas_kanade.html#lucas-kanade
'''
import numpy as np
import cv2
import Utility as MyUtility

'''
Apply Lucas-Kanade tracking algorithm
'''
class lkTracking(object):
    
    '''Construction function'''
    def __init__(self):
        
        #initialize instance variable
        self.tracks = []
        self.track_len = 10
        self.frame_idx = 0
        self.detect_interval = 5
        
        self.lk_params = dict( winSize  = (15, 15),
                               maxLevel = 2,
                               criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        self.feature_params = dict( maxCorners = 500,
                                    qualityLevel = 0.3,
                                    minDistance = 7,
                                    blockSize = 7 )
        
    def Run(self, _frame, _found_object=[]):
        #get gray frame
        frame_gray = cv2.cvtColor(_frame, cv2.COLOR_BGR2GRAY)
        #copy frame for result
        vis = _frame.copy()
        
        self.frame_idx += 1
        
        if len(self.tracks) > 0:
            img0, img1 = self.prev_gray, frame_gray
            p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
            p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **self.lk_params)
            p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **self.lk_params)
            d = abs(p0-p0r).reshape(-1, 2).max(-1)
            good = d < 1
            new_tracks = []
            for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
                if not good_flag:
                    continue
                tr.append((x, y))
                #remove oldest data node from head of queue when tracking data become to upper bound-self.track_len
                if len(tr) > self.track_len:
                    del tr[0]
                new_tracks.append(tr)
                cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)
            self.tracks = new_tracks
            cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))
        
        #refresh the found feature points at every self.detect_interval frames    
        if self.frame_idx % self.detect_interval == 0:
            mask = np.zeros_like(frame_gray)
            mask[:] = 255
            for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                cv2.circle(mask, (x, y), 5, 0, -1)
            p = cv2.goodFeaturesToTrack(frame_gray, mask = mask, **self.feature_params)
            if p is not None:
                for x, y in np.float32(p).reshape(-1, 2):
                    self.tracks.append([(x, y)])
                    
            self.frame_idx = 0
        
        #filter self.tracks under objects to remove redundant points
        '''filter_track=[]
        for rect in _found_object:
            for tr in self.tracks:
                if(MyUtility.Utilities.pointDistance(MyUtility.Utilities.rectCenter(rect),tr[-1])>100):
                    continue
                #if((tr not in filter_track) and (MyUtility.Utilities.pointInside(tr[-1], rect))):
                if(tr not in filter_track):
                    filter_track.append(tr)
                    break
        self.tracks = filter_track'''
        self.prev_gray = frame_gray
    
        return vis

'''
Apply Camshift tracking algorithm
'''
class  CamshiftTracking(object): 
    '''Construction function'''
    def __init__(self):
        #initialize instance variable
        self.isInit=0                
    
    def Run(self,_frame, _rect):
        #get value of rectangle to set track_window
        c,r,w,h = _rect
        r=r-h 
         
        # setup initial location of window
        if(self.isInit==0):                 
            #self.track_window 
            self.track_window = (c,r,w,h)
        
            # set up the ROI for tracking
            roi = _frame[r:r+h, c:c+w]
            hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
            self.roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
            cv2.normalize(self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)
            
            # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
            self.term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
            #finish initialize
            self.isInit=1
            
        #reset self.track_window
        '''elif(MyUtility.Utilities.centerRectDistance(_rect, self.track_window)<100 or 
             MyUtility.Utilities.rectArea(self.track_window)>10000):
            #self.track_window 
            self.track_window = (c,r,w,h)
        
            # set up the ROI for tracking
            roi = _frame[r:r+h, c:c+w]
            hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
            self.roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
            cv2.normalize(self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)
            
            # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
            self.term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )'''

        hsv = cv2.cvtColor(_frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv],[0], self.roi_hist,[0,180],1)

        # apply CamShift to get the new location
        ret, self.track_window = cv2.CamShift(dst, self.track_window, self.term_crit)

        # Draw it on image
        pts = cv2.boxPoints(ret)
        pts = np.int0(pts)
        
        #plot rectangle
        _frame = cv2.polylines(_frame,[pts],True, 255,1)


'''
Apply Meanshift tracking algorithm
'''    
class  MeanshiftTracking(object): 
    '''Construction function'''
    def __init__(self):
        #initialize instance variable
        self.isInit=0
        
    def Run(self,_frame, _rect):            
        #get value of rectangle to set track_window
        c,r,w,h = _rect 
        r=r-h
    
        # setup initial location of window
        if(self.isInit==0):                 
            #set self.track_window
            self.track_window = (c,r,w,h)
        
            # set up the ROI for tracking
            roi = _frame[r:r+h, c:c+w]
            hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
            self.roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
            cv2.normalize(self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)
            
            # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
            self.term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
            
            self.isInit=1
        #reset self.track_window
        '''elif(MyUtility.Utilities.centerRectDistance(_rect, self.track_window)>100):
            #set self.track_window
            self.track_window = (c,r,w,h)
            
            # set up the ROI for tracking
            roi = _frame[r:r+h, c:c+w]
            hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
            self.roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
            cv2.normalize(self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)'''

        hsv = cv2.cvtColor(_frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv],[0],self.roi_hist,[0,180],1)

        # apply CamShift to get the new location
        ret, self.track_window = cv2.meanShift(dst, self.track_window, self.term_crit)

        # Draw it on image
        x,y,w,h = self.track_window
        cv2.rectangle(_frame, (x,y), (x+w,y+h), 255,1)

'''
define class to label founded objects
'''
class LabeledObject(object):
    '''ObjTracking construction function'''
    def __init__(self):
        self.idx=0
        self.rect=[]
        self.tracks=[]
        self.isActive=0
        # wait 5 frame to check timeout, then set isActive=0 to inactive moving object
        self.activeTimeout=5
        #generate random color
        self.color=np.random.randint(0,255,(1,3))


'''
Object tracking class
'''        
class ObjTracking(object):    

    '''ObjTracking construction function'''
    def __init__(self):
        #initialize instance variable
        self.track_seeds=0
        self.objtracks = []
        self.track_len = 10
        self.frame_idx = 0
        self.detect_interval = 5
        self.timeout = 5       
            
    #create new LabeledObject() instance
    def newObjTrack(self, _rect):
        #new LabeledObject instance
        lb_object=LabeledObject()
        
        #generate id for lb_object
        self.track_seeds+=1
        lb_object.idx=self.track_seeds
        
        #set current rectangle data
        lb_object.rect=_rect
        
        #set head of track data as center of rectangle
        lb_object.tracks.append(MyUtility.Utilities.rectCenter(_rect))
        
        #set activate state
        lb_object.isActive=1
        
        #return new tracking object instance
        return lb_object
    
    #update LabeledObject() instance by appending new point to tracking list
    def updateObjTrack(self, _lb_object, _rect):  
        #set current rectangle data
        _lb_object.rect=_rect
        
        #append center of rectangle to lb_object.tracks list
        _lb_object.tracks.append(MyUtility.Utilities.rectCenter(_rect))
        
        #refresh activeTimeout with default value in timeout
        _lb_object.activeTimeout=self.timeout
    
    #delete inactive LabeledObject() instance from tracking list
    def deleteObjTrack(self): 
        for i, lb_object in enumerate(self.objtracks):
            if(lb_object.isActive==0):
                del self.objtracks[i] 
    
    def Run(self, _frame, _found_object, _minDist=100, _drawMode=MyUtility.DrawTpye.Default, _thickness = 1):
        #saved tracked objects in _found_object
        old_tracks=[]            
        #self.tracks is not empty, update self.tracks
        for lb_object in self.objtracks:
            if(lb_object.isActive==0):
                continue
            
            minDistance =_minDist
            minRect = []
            #for each object to check tracking information
            for rect in _found_object:
                #get center of rect
                cen_x, cen_y = MyUtility.Utilities.rectCenter(rect)
                ox, oy = lb_object.tracks[-1]
                
                #if center of rect within tracked object, then update track data of tracked object
                if(MyUtility.Utilities.pointDistance((cen_x, cen_y),(ox, oy))<_minDist):
                    #add old_tracks list
                    old_tracks.append(rect)
                    #get minDistance and minRect                
                    if(MyUtility.Utilities.pointDistance((cen_x, cen_y),(ox, oy))<minDistance):
                        minDistance = MyUtility.Utilities.pointDistance((cen_x, cen_y),(ox, oy))
                        minRect = rect

            #add rect with minimum distance to tracks
            if(minRect != []):
                self.updateObjTrack(lb_object,minRect)
            
        #for each object to add new track object to self.tracks
        for rect in _found_object:
            if(rect not in old_tracks):
                #add lb_object to self.tracks
                self.objtracks.append(self.newObjTrack(rect))
        
        #for each object to update active state and timeout
        for obj in self.objtracks:
            if(obj.isActive==0):
                continue
            
            #update activeTimeout and check isActive state
            if(obj.activeTimeout==0):
                obj.isActive=0
            else:
                #calculate activeTimeout
                obj.activeTimeout-=1
            
            #For those overlap objects, merge to one object by changing isActive state
            for obj_t in self.objtracks:
                if(obj.idx < obj_t.idx and obj.tracks[-1]==obj_t.tracks[-1]):
                    obj_t.isActive=0

            # draw the tracking information on the frame
            if(len(obj.tracks)>0):
                MyUtility.Utilities.draw_tracking(_frame, obj, _drawMode, _thickness)
        
        #delete inactive object from tracking list       
        self.deleteObjTrack()
              
if __name__ == '__main__':
    pass