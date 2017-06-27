'''
This demo shows how to play video from stream file
'''

import cv2
import sys

#input argument verification
if(len(sys.argv)<2):
    print("Video stream file cannot be found!")
    exit()

#get stream file
fname=sys.argv[1]

''''
To capture a video, you need to create a VideoCapture object. 
Its argument can be either the device index or the name of a video file
'''
cap = cv2.VideoCapture(fname)

#Check whether video stream open successful or not
while(cap.isOpened()):
    ret, frame = cap.read()

    cv2.imshow('frame',frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    #control playback speed, 3ms for each frame
    cv2.waitKey (3)

cap.release()
cv2.destroyAllWindows()
