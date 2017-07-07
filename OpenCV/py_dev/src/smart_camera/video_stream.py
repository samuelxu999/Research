"""
========================
Video Stream.
========================
Created on June 26, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide video stream related function.
@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html#display-video
"""

import time
import datetime
import cv2
import os.path
import object_detect
from enum import Enum
from matplotlib.pyplot import switch_backend


# Define detect mode
class DetectionMode(Enum):
    NoDetection = 0 
    Face = 1
    Eyes = 2
    Body = 3
    Motion = 4 

# Define for stream type: camera or video files
class StreamType(Enum):
    Camera = 0 
    Video = 1
    

# Define detect mode
class RecordMode(Enum):
    NoRecord = 0 
    VideoRecord = 1
    PictureSnap = 2 

    
'''
@Function: Video stream handler, such as open camera and preview, playback video, save camera video.
'''
class VideoStream(object):
   
    '''ObjDetect construction function'''
    def __init__(self):
        #super().__init__()  
        self.cap=""
    
    
    '''
    This function will initialize cap by using cv2.VideoCapture
    @camera_id: camera index, start from 0.
    '''  
    def set_Cap(self,video_src):
        ''''
        To capture a video, you need to create a VideoCapture object. 
        Its argument can be either the device index or the name of a video file
        '''
        self.cap = cv2.VideoCapture(video_src)
    
    '''
    This function will return frame by using VideoCapture::read()
    @camera_id: camera index, start from 0.
    '''  
    def get_Frame(self):
        if(self.cap.isOpened()):
            ret, frame = self.cap.read()
        else:
            ret, frame = [False, 0]
        return ret, frame
    
    
    '''
    This function play stream based on 
    @_streamType: StreamType.Camera or StreamType.Video.
    @_frame_freq: set frame frequency for previewing, default value is 1. 
    @_recordmode: define record mode: video recording(only support StreamType.Camera) or picture snap.
    @_streamSrc: video file path.
    @_streamDes: destination path to save record.
    '''  
    def StreamPreviewer(self, _streamType=StreamType.Camera, 
                        _frame_freq=1, _recordmode=RecordMode.NoRecord, 
                        _streamSrc='', _streamDes=''):
        if(_streamType==StreamType.Camera):
            #initialize VideoCapture
            self.set_Cap(0)
        elif(_streamType==StreamType.Video):
            #verify video file path
            if(not os.path.isfile(_streamSrc)):
                print("Video %s is not exist!"  %(_streamSrc))
                return
            #print(StreamType.Video.value)
            self.set_Cap(_streamSrc)
        else:
            print("Not supported stream mode, please use StreamType.Camera or StreamType.Video")
        
        #if use camera type and set record mode, then check _streamDes path validation            
        if((_recordmode==RecordMode.VideoRecord) and (_streamType==StreamType.Camera)):
            folder,filename=os.path.split(_streamDes);
            #check whether destination folder is exist
            if(not os.path.exists(folder)):
                print("Record  save path: %s is not exist!"  %(folder))
                return
            # Define the codec and create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(_streamDes,fourcc, 20.0, (640,480))
        
        #Check whether cap is opened successful.
        if(not self.cap.isOpened()):
            print("Stream source is not available!")
            return
        
        while(True):
            # Capture frame-by-frame
            ret, frame = self.get_Frame()
            
            #verify frame
            if(not ret):
                print("No frame, exit program!")
                break
            
            '''cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)'''
            
            # Display the resulting frame
            cv2.imshow('Stream Previewer',frame)
            
            if(_recordmode==RecordMode.PictureSnap):
                #press key 'c' to save frame as %time.png 
                if cv2.waitKey(1) & 0xFF == ord('c'):
                    mytime=datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")
                    cv2.imwrite(mytime+'.png',frame)
                    #print(mytime+'.png')
            elif((_recordmode==RecordMode.VideoRecord) and (_streamType==StreamType.Camera)):
                # write the frame
                out.write(frame)
            
            #frame refresh rate: cv2.waitKey(1) means 1ms
            #press "q" will quit video show
            if cv2.waitKey(_frame_freq) & 0xFF == ord('q'):
                break
            
        # When everything done, release the capture
        self.cap.release()
        if((_recordmode==RecordMode.VideoRecord) and (_streamType==StreamType.Camera)):
            out.release()
        cv2.destroyAllWindows()
    
    '''
    This function will process stream frame and apply feature detection 
    @_streamType: StreamType.Camera or StreamType.Video.
    @_frame_freq: set frame frequency for previewing, default value is 1. 
    @_detectmode: define detect mode
    @_detect_freq: set how many frames interval for each detect
    @_streamSrc: video file path.
    @_motionmethod: define motion detect method
    ''' 
    def StreamDetection(self, _streamType=StreamType.Camera, _frame_freq=1,
                        _detectmode=DetectionMode.NoDetection, _detect_freq=1, 
                        _streamSrc='',_motionmethod=object_detect.MotionMethod.Diff):
        
        if(_streamType==StreamType.Camera):
            #initialize VideoCapture
            self.set_Cap(0)
        elif(_streamType==StreamType.Video):
            #verify video file path
            if(not os.path.isfile(_streamSrc)):
                print("Video %s is not exist!"  %(_streamSrc))
                return
            #print(StreamType.Video.value)
            self.set_Cap(_streamSrc)
        else:
            print("Not supported stream mode, please use StreamType.Camera or StreamType.Video")
        
        #Check whether cap is opened successful.
        if(not self.cap.isOpened()):
            print("Stream source is not available!")
            return
        
        if(_detectmode!=DetectionMode.NoDetection):
            #initialize object_detect instance        
            myObjDetect=object_detect.ObjDetect()
        
        #initialize detect_date
        detect_rate=0
        
        if(_detectmode==DetectionMode.Motion):
            # initialize the first frame in the video stream
            backgroundFrame = None
        
        while(True):
            # Capture frame-by-frame
            ret, frame = self.get_Frame()
            
            #verify frame
            if(not ret):
                print("No frame, exit program!")
                break
            
            '''cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)'''
           
            detect_rate+=1
            object_count=0
            if((detect_rate%int(_detect_freq))==0):                
                if(_detectmode==DetectionMode.Face):
                    #detect face 
                    frame, faces = myObjDetect.detect_face(frame)
                    object_count = len(faces)
                elif(_detectmode==DetectionMode.Eyes):
                    frame = myObjDetect.detect_eye(frame)
                elif(_detectmode==DetectionMode.Body):
                    object_count = myObjDetect.detectBody(frame)
                elif(_detectmode==DetectionMode.Motion):
                    if(backgroundFrame is None):
                        # resize the frame, convert it to grayscale, and blur it
                        #frame = cv2.imread('./backgroundframe.png')
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        gray = cv2.GaussianBlur(gray, (21, 21), 0)
                        backgroundFrame = gray
                    else:
                        if(_motionmethod==object_detect.MotionMethod.Diff):
                            backgroundFrame,object_count = myObjDetect.detectMotionDiff(backgroundFrame, frame, 100, object_detect.MotionType.Static)
                        else:
                            object_count = myObjDetect.detectMotionMOG(frame, 2000, _motionmethod)
                else:
                    pass
                detect_rate=0
            
            # draw the detect object count on the frame
            cv2.putText(frame, "Detect: {}".format(object_count), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2) 
               
            # Display the resulting frame
            cv2.imshow('Stream Detector',frame)
            
            #frame refresh rate: cv2.waitKey(1) means 1ms
            #press "q" will quit video show
            if cv2.waitKey(_frame_freq) & 0xFF == ord('q'):
                break
                
        # When everything done, release the capture
        self.cap.release()
        cv2.destroyAllWindows()                 

        
def test_fun():
    filesrc0='../../res/vtest.avi'
    filesrc1='E:\Video_20170612\EC-Main-Entrance-2017-05-21_02h10min05s000ms.mp4'
    filesrc2='E:\Video_20170612\EC-Main-Entrance-out.mp4'
    
    myVideo=VideoStream()
    #myVideo.StreamPreviewer(StreamType.Camera, 1, RecordMode.VideoRecord,'','./test.avi')
    #myVideo.StreamPreviewer(StreamType.Camera, 1, RecordMode.PictureSnap)    
    #myVideo.StreamPreviewer(StreamType.Video, 33, RecordMode.PictureSnap, '../../res/vtest.avi')
    
    
    #myVideo.StreamDetection(StreamType.Video,1,DetectionMode.Face,1,'./test.avi')
    #myVideo.StreamDetection(StreamType.Video,1,DetectionMode.Body,1,'../../res/vtest.avi')
    myVideo.StreamDetection(StreamType.Video,33,DetectionMode.Motion,1,filesrc2,object_detect.MotionMethod.MOG)
    
    #myVideo.StreamDetection(StreamType.Camera,33,DetectionMode.Motion,1,'',object_detect.MotionMethod.MOG2)
    #myVideo.StreamDetection(StreamType.Camera,1,DetectionMode.Face,1)

        
if __name__ == "__main__":
    test_fun()
        

