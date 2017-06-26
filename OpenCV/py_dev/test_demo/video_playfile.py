import cv2
import sys


fname=sys.argv[1]

cap = cv2.VideoCapture(fname)

while(cap.isOpened()):
    ret, frame = cap.read()

    cv2.imshow('frame',frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
