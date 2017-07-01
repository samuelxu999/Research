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

import cv2
import os.path
import object_detect

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
    This function will capture video from camera
    @camera_id: camera index, start from 0.
    '''   
    def camera_Previewer(self, camera_id):
        
        #initialize VideoCapture
        self.set_Cap(int(camera_id))
        
        #Check whether cap is opened successful.
        if(not self.cap.isOpened()):
            print("Camera is not available!")
            return
                
        while(True):
            # Capture frame-by-frame
            ret, frame = self.get_Frame()
            
            #verify frame
            if(not ret):
                print("No frame from camera!")
                break
            
            # Display the resulting frame
            cv2.imshow('Camera Player',frame)
            
            #frame refresh rate: cv2.waitKey(1) means 1ms
            #press "q" will quit video show
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        # When everything done, release the capture
        self.cap.release()
        cv2.destroyAllWindows()
       
 
    '''
    This function will capture video from camera and save as file
    @camera_id: camera index, start from 0.
    '''   
    def camera_Videosave(self, camera_id, video_file):
        
        #initialize VideoCapture
        self.set_Cap(int(camera_id))
        
        #Check whether cap is opened successful.
        if(not self.cap.isOpened()):
            print("Camera is not available!")
            return
        
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(video_file,fourcc, 20.0, (640,480))
                
        while(self.cap.isOpened()):
            # Capture frame-by-frame
            ret, frame = self.get_Frame()
            
            #verify frame
            if ret==True:        
                # write the frame
                out.write(frame)
                
                #show live frame
                cv2.imshow('frame',frame)
                if cv2.waitKey(33) & 0xFF == ord('q'):
                    break
            else:
                print("No frame from camera!")
                break
            
        # When everything done, release the capture
        self.cap.release()
        out.release()
        cv2.destroyAllWindows()
        
    '''
    This function will capture video from camera
    @video_file: video file path.
    '''   
    def video_Player(self, video_file):
        
        if(not os.path.isfile(video_file)):
            print("Video %s is not exist!"  %(video_file))
            return
        
        #initialize VideoCapture
        self.set_Cap(video_file)
        
        #Check whether cap is opened successful.
        if(not self.cap.isOpened()):
            print("Video could not open!"  %(video_file))
            return
                        
        while(True):
            # Capture frame-by-frame
            ret, frame = self.get_Frame()
            
            #verify frame
            if(not ret):
                print("No frame from video!")
                break
            
            # Display the resulting frame
            cv2.imshow('Video Player',frame)
            
            #frame refresh rate: cv2.waitKey(3) means 3ms
            #press "q" will quit video show
            if cv2.waitKey(33) & 0xFF == ord('q'):
                break
            
        # When everything done, release the capture
        self.cap.release()
        cv2.destroyAllWindows()
        
    '''
    This function will capture video from camera and detect faces
    @camera_id: camera index, start from 0.
    '''   
    def camera_FaceDetect(self, camera_id, detect_freq):
        
        #initialize VideoCapture
        self.set_Cap(int(camera_id))
        
        #initialize object_detect instance        
        myObjDetect=object_detect.ObjDetect()
        
        #Check whether cap is opened successful.
        if(not self.cap.isOpened()):
            print("Camera is not available!")
            return
        
        detect_rate=0
        
        while(True):
            # Capture frame-by-frame
            ret, frame = self.get_Frame()
            
            #verify frame
            if(not ret):
                print("No frame from camera!")
                break
            
            detect_rate+=1
            
            if((detect_rate%int(detect_freq))==0):
                #detect face 
                frame, faces = myObjDetect.detect_face(frame)
                #frame = myObjDetect.detect_eye(frame)
                detect_rate=0
           
            # Display the resulting frame
            cv2.imshow('Camera Player',frame)
            
            #frame refresh rate: cv2.waitKey(1) means 1ms
            #press "q" will quit video show
            if cv2.waitKey(33) & 0xFF == ord('q'):
                break
            
        # When everything done, release the capture
        self.cap.release()
        cv2.destroyAllWindows()
        
    '''
    This function will capture video from camera and detect faces.
    @video_file: video file path.
    '''   
    def video_FaceDetect(self, video_file, detect_freq):
        
        if(not os.path.isfile(video_file)):
            print("Video %s is not exist!"  %(video_file))
            return
        
        #initialize VideoCapture
        self.set_Cap(video_file)
        
        #initialize object_detect instance        
        myObjDetect=object_detect.ObjDetect()
        
        #Check whether cap is opened successful.
        if(not self.cap.isOpened()):
            print("Video could not open!"  %(video_file))
            return
        
        detect_rate=0
                        
        while(True):
            # Capture frame-by-frame
            ret, frame = self.get_Frame()
            
            #verify frame
            if(not ret):
                print("No frame from video!")
                break
            
            detect_rate+=1
            
            if((detect_rate%int(detect_freq))==0):
                #detect face 
                frame, faces = myObjDetect.detect_face(frame)
                #frame = myObjDetect.detect_eye(frame)
                detect_rate=0
            
            # Display the resulting frame
            cv2.imshow('Video Player',frame)
            
            #frame refresh rate: cv2.waitKey(3) means 3ms
            #press "q" will quit video show
            if cv2.waitKey(33) & 0xFF == ord('q'):
                break
            
        # When everything done, release the capture
        self.cap.release()
        cv2.destroyAllWindows()
        
def test_fun():
    myVideo=VideoStream()
    #myVideo.camera_Previewer(0)
    #myVideo.video_Player("E:\Video_20170612\EC-Main-Entrance-out.mp4")
    #myVideo.camera_Videosave(0, "./test.avi")
    myVideo.camera_FaceDetect(0, 10)
    #myVideo.video_FaceDetect("E:\Video_20170612\EC-Main-Entrance-in.mp4", 10)
        
if __name__ == "__main__":
    #process("kobe.bmp")
    test_fun()
        

