'''
This demo shows how to capture video from camera:
http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
'''

import cv2

''''
To capture a video, you need to create a VideoCapture object. 
Its argument can be either the device index or the name of a video file
'''
cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('Video Player',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    cv2.waitKey(3)
    
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
