import os
import cv2

'''Detect face related feature by using cv2.CascadeClassifier'''
def detect_face():
    #face_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml')
    #eye_cascade = cv2.CascadeClassifier('/usr/local/share/OpenCV/haarcascades/haarcascade_eye.xml')
    face_cascade = cv2.CascadeClassifier('D:\ProgramFiles\opencv_3.2_dev\sources\opencv\data\haarcascades\haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier('D:\ProgramFiles\opencv_3.2_dev\sources\opencv\data\haarcascades\haarcascade_eye.xml')

    img = cv2.imread('../../res/groupface.jpg')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex,ey,ew,eh) in eyes:
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
    
    cv2.imshow('Face_Detect',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
  
    '''grayscale = cv.CreateImage((image.width, image.height), 8, 1)
    cv.CvtColor(image, grayscale, cv.CV_BGR2GRAY)
    
    cascade = cv.Load("/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_alt_tree.xml")
    rect = cv.HaarDetectObjects(grayscale, cascade, cv.CreateMemStorage(), 1.1, 2,
    cv.CV_HAAR_DO_CANNY_PRUNING, (20,20))
    
    result = []
    for r in rect:
      result.append((r[0][0], r[0][1], r[0][0]+r[0][2], r[0][1]+r[0][3]))
    return result'''

def process(infile):
  
    #image = cv.imread(infile);
    #print(len(image))
    #if(image!=[]):
    #  faces = detect_object(image)
    #im = Image.open(infile)
    path = os.path.abspath(infile)
    save_path = os.path.splitext(path)[0]+"_face"
    print(path)
    print(save_path)
    '''try:
      os.mkdir(save_path)
    except:
      pass'''

def test():
    img = cv2.imread("../../res/kobe.bmp")   
    cv2.namedWindow("Image")   
    cv2.imshow("Image", img)   
    cv2.waitKey (0)  
    cv2.destroyAllWindows()

if __name__ == "__main__":
    #process("kobe.bmp")
    #test()
    detect_face()
    #test()
  
