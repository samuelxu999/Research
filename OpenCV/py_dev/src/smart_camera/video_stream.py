'''
========================
Video Stream.
========================
Created on June 26, 2017
@author: Xu Ronghua
@Email:  rxu22@binghamton.edu
@TaskDescription: This module provide video stream related function.
@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html#display-video
'''

import datetime
import cv2
import os.path
from enum import Enum

import Utility as MyUtility
import object_detect as ObjDetect
import flow_tracking as flowTrack


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
    @_minArea: input minimum area of contour to filter noise
    @_minDist: input minimum distance around tracking object to update tracking path
    ''' 
    def StreamDetection(self, _streamType=StreamType.Camera, _frame_freq=1,
                        _detectmode=DetectionMode.NoDetection, _detect_freq=1, 
                        _streamSrc='',_motionmethod=ObjDetect.MotionMethod.Diff, _minArea=100, _minDist=50):
        
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
            #initialize object detect instance        
            myObjDetect=ObjDetect.ObjDetect()
            
            #initialize object tracking instance  
            myObjTrack =flowTrack.ObjTracking()
            myLkTrack = flowTrack.lkTracking()
            myMeanshift = flowTrack.MeanshiftTracking()
            myCamshift = flowTrack.CamshiftTracking()
            myMultiTracker =flowTrack.MultiTracker()
            
        #initialize detect_date
        detect_rate=0
        frame_id=0
        
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
            
            #resize frame solution to optimize performance
            #dim = (640, 480)
            #frame = cv2.resize(frame, dim, interpolation = cv2.INTER_CUBIC)
            
            '''cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)'''
            
            frame_id+=1
            
            #=========================== object detect and classification================================
            detect_rate+=1
            #clear found_objects
            found_objects=[]
            human_objects=[]
            if((detect_rate%int(_detect_freq))==0):                
                if(_detectmode==DetectionMode.Face):
                    #detect face 
                    frame, found_objects = myObjDetect.detect_face(frame)
                elif(_detectmode==DetectionMode.Eyes):
                    frame = myObjDetect.detect_eye(frame)
                elif(_detectmode==DetectionMode.Body):
                    found_objects = myObjDetect.detectBody(frame)
                elif(_detectmode==DetectionMode.Motion):
                    if(backgroundFrame is None):
                        # resize the frame, convert it to grayscale, and blur it
                        #frame = cv2.imread('./backgroundframe.png')
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        gray = cv2.GaussianBlur(gray, (21, 21), 0)
                        backgroundFrame = gray
                    else:
                        if(_motionmethod==ObjDetect.MotionMethod.Diff):
                            backgroundFrame,found_objects = myObjDetect.detectMotionDiff(backgroundFrame, frame, _minArea, ObjDetect.MotionType.Static)
                        else:
                            found_objects = myObjDetect.detectMotionMOG(frame, _minArea, _motionmethod)
                            '''human_objects = myObjDetect.detectHuman(frame,found_objects)
                            print(human_objects)'''
                            #Apply Lucas-Kanade tracking method
                            #frame = myLkTrack.Run(frame, found_objects)
                            #drawmode=MyUtility.DrawType.LabelText.value|MyUtility.DrawType.PolyLines.value|MyUtility.DrawType.Rect.value|MyUtility.DrawType.Center.value
                            #myObjTrack.Run(frame, found_objects, _minDist, drawmode, 2)
                            #myMultiTracker.Run(frame, found_objects, _minDist, drawmode, 2)
                            
                            if(len(found_objects)>1):                                
                                #cen_x, cen_y=MyUtility.Utilities.rectCenter(found_objects[1])
                                #myMeanshift.Run(frame, (int(cen_x-5),int(cen_y),10,5))
                                #myCamshift.Run(frame, (int(cen_x-10),int(cen_y-10),20,20))
                                #myMeanshift.Run(frame, found_objects[0])
                                #myCamshift.Run(frame, found_objects[0])
                                pass
                else:
                    pass
                #reset detect_rate
                detect_rate=0
            
            #====================================== object tracking ============================================ 
            drawmode=MyUtility.DrawType.LabelText.value|MyUtility.DrawType.PolyLines.value|MyUtility.DrawType.Rect.value|MyUtility.DrawType.Center.value
            #myObjTrack.Run(frame, found_objects, _minDist, drawmode, 2)
            myMultiTracker.Run(frame, found_objects, _minDist, drawmode, 2)
            
            
            object_count=len(found_objects) 
            #track_count=len(myObjTrack.objtracks)
            track_count=len(myMultiTracker.objtracks)           
            
            #draw bounding box for detected objects    
            drawmode=MyUtility.DrawType.Rect.value|MyUtility.DrawType.Center.value
            #MyUtility.Utilities.draw_detections(frame, found_objects, (0,255,0), 2, drawmode)
            
            # draw the surveillance information on the frame
            cv2.putText(frame, "Frame ID: {}".format(frame_id), (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                        
            cv2.putText(frame, "Detect: {}".format(object_count), (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)   
            
            cv2.putText(frame, "Tracking: {}".format(track_count), (10, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)          
            
            # Resize image if necessary
            #frame = cv2.resize(frame, (1024, 768))   
            # Display the resulting frame
            cv2.imshow('Stream Detector',frame)
            '''if(detect_rate==0):
                cv2.imwrite('./testresult/tracking/'+str(frame_id)+'.png',frame)'''
            #print('./testresult/'+str(frame_id)+'.png')
            
            #frame refresh rate: cv2.waitKey(1) means 1ms
            #press "q" will quit video show
            if(cv2.waitKey(_frame_freq) & 0xFF == ord('q')):
                break
                
        # When everything done, release the capture
        self.cap.release()
        cv2.destroyAllWindows()                 

        
def test_fun():
    filesrc0='../../res/vtest.avi'
    filesrc1='E:/Video_20170612/EC-Main-Entrance-2017-05-21_02h10min05s000ms.mp4'
    filesrc2='E:/Video_20170612/EC-Main-Entrance-out.mp4'
    filesrc3='D:/dji_album/DJI_0036.mp4'
    filesrc4='D:/dji_album/traffic/DJI_0001.mp4'
    
    myVideo=VideoStream()
    #myVideo.StreamPreviewer(StreamType.Camera, 1, RecordMode.VideoRecord,'','./test.avi')
    #myVideo.StreamPreviewer(StreamType.Camera, 1, RecordMode.PictureSnap)    
    #myVideo.StreamPreviewer(StreamType.Video, 33, RecordMode.PictureSnap, filesrc0)
    
    
    #myVideo.StreamDetection(StreamType.Video,1,DetectionMode.Face,1,filesrc2)
    myVideo.StreamDetection(StreamType.Video,1,DetectionMode.Body,5,filesrc0, ObjDetect.MotionMethod.MOG2, 100, 50)
    #myVideo.StreamDetection(StreamType.Video,1,DetectionMode.Motion,1,filesrc0,ObjDetect.MotionMethod.MOG2, 200, 60)
    
    #myVideo.StreamDetection(StreamType.Camera,33,DetectionMode.Motion,1,'',object_detect.MotionMethod.MOG2)
    #myVideo.StreamDetection(StreamType.Camera,1,DetectionMode.Face,1)

        
if __name__ == "__main__":
    test_fun()
        

