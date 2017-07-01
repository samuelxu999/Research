'''
Created on 2017.07.01

@author: Ronghua Xu        
@Function: Video Analysis
1) Meanshift and Camshift
2) Optical Flow
3) Background Subtraction
@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_video/py_meanshift/py_meanshift.html#meanshift
'''

import numpy as np
import cv2

def Meanshift():
    cap = cv2.VideoCapture(0)

    # take first frame of the video
    ret,frame = cap.read()
    
    # setup initial location of window
    r,h,c,w = 250,90,400,125  # simply hardcoded the values
    track_window = (c,r,w,h)
    
    # set up the ROI for tracking
    roi = frame[r:r+h, c:c+w]
    hsv_roi =  cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
    roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
    
    # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
    term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
    
    while(1):
        ret ,frame = cap.read()
    
        if ret == True:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)
    
            # apply meanShift to get the new location
            ret, track_window = cv2.meanShift(dst, track_window, term_crit)
    
            # Draw it on image
            x,y,w,h = track_window
            img2 = cv2.rectangle(frame, (x,y), (x+w,y+h), 255,2)
            cv2.imshow('meanShift',img2)
    
            k = cv2.waitKey(60) & 0xff
            if k == 27:
                break
            '''else:
                cv2.imwrite(chr(k)+".jpg",img2)'''
    
        else:
            break
    
    cv2.destroyAllWindows()
    cap.release()

def Camshift():
    cap = cv2.VideoCapture(0)

    # take first frame of the video
    ret,frame = cap.read()
    
    # setup initial location of window
    r,h,c,w = 250,90,400,125  # simply hardcoded the values
    track_window = (c,r,w,h)
    
    # set up the ROI for tracking
    roi = frame[r:r+h, c:c+w]
    hsv_roi =  cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
    roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
    
    # Setup the termination criteria, either 10 iteration or move by atleast 1 pt
    term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
    
    while(1):
        ret ,frame = cap.read()
    
        if ret == True:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)
    
            # apply CamShift to get the new location
            ret, track_window = cv2.CamShift(dst, track_window, term_crit)
    
            # Draw it on image
            pts = cv2.boxPoints(ret)
            pts = np.int0(pts)
            img2 = cv2.polylines(frame,[pts],True, 255,2)
            cv2.imshow('CamShift',img2)
    
            k = cv2.waitKey(60) & 0xff
            if k == 27:
                break
            elif k == ord('s'):
                cv2.imwrite(chr(k)+".jpg",img2)
    
        else:
            break
    
    cv2.destroyAllWindows()
    cap.release()

def LucasKanadeOpticalFlow():
    #cap = cv2.VideoCapture("E:\Video_20170612\EC-Main-Entrance-in.mp4")
    cap = cv2.VideoCapture("../../res/vtest.avi")

    # params for ShiTomasi corner detection
    feature_params = dict( maxCorners = 100,
                           qualityLevel = 0.3,
                           minDistance = 7,
                           blockSize = 7 )
    
    # Parameters for lucas kanade optical flow
    lk_params = dict( winSize  = (15,15),
                      maxLevel = 2,
                      criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    
    # Create some random colors
    color = np.random.randint(0,255,(100,3))
    
    # Take first frame and find corners in it
    ret, old_frame = cap.read()
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)
    
    # Create a mask image for drawing purposes
    mask = np.zeros_like(old_frame)
    
    while(1):
        ret,frame = cap.read()
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        # calculate optical flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    
        # Select good points
        good_new = p1[st==1]
        good_old = p0[st==1]
    
        # draw the tracks
        for i,(new,old) in enumerate(zip(good_new,good_old)):
            a,b = new.ravel()
            c,d = old.ravel()
            mask = cv2.line(mask, (a,b),(c,d), color[i].tolist(), 2)
            frame = cv2.circle(frame,(a,b),5,color[i].tolist(),-1)
        img = cv2.add(frame,mask)
    
        cv2.imshow('Lucas Kanade Optical Flow',img)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
    
        # Now update the previous frame and previous points
        old_gray = frame_gray.copy()
        p0 = good_new.reshape(-1,1,2)
    
    cv2.destroyAllWindows()
    cap.release()

def DenseOpticalFlow():
    #cap = cv2.VideoCapture("E:\Video_20170612\EC-Main-Entrance-in.mp4")
    cap = cv2.VideoCapture("../../res/vtest.avi")
    

    ret, frame1 = cap.read()
    prvs = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
    hsv = np.zeros_like(frame1)
    hsv[...,1] = 255
    
    while(1):
        ret, frame2 = cap.read()
        next = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
    
        flow = cv2.calcOpticalFlowFarneback(prvs,next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    
        mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
        hsv[...,0] = ang*180/np.pi/2
        hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
        rgb = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
    
        cv2.imshow('Dense Optical Flow',rgb)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
        elif k == ord('s'):
            cv2.imwrite('opticalfb.png',frame2)
            cv2.imwrite('opticalhsv.png',rgb)
        prvs = next
    
    cap.release()
    cv2.destroyAllWindows()

def BackgroundSubtractorMOG():
    cap = cv2.VideoCapture('../../res/vtest.avi')

    #fgbg = cv2.createBackgroundSubtractorKNN()
    fgbg = cv2.createBackgroundSubtractorMOG2()

    while(1):
        ret, frame = cap.read()
    
        fgmask = fgbg.apply(frame)
    
        cv2.imshow('BackgroundSubtractorMOG2',fgmask)
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    #Meanshift()
    #Camshift()
    #LucasKanadeOpticalFlow()
    #DenseOpticalFlow()
    BackgroundSubtractorMOG()
    