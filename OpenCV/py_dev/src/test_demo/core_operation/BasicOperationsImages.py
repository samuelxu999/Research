'''
Created on 2017.07.03

@author: Ronghua Xu        
'''

import cv2
from matplotlib import pyplot as plt

'''
@Function: Basic Operations on Images
Access pixel values and modify them
Access image properties
Setting Region of Image (ROI)
Splitting and Merging images
@Reference: https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_core/py_basic_ops/py_basic_ops.html#basic-ops
'''

def AccessingModifyingpixelvalues():
    #load image
    img = cv2.imread('../../../res/messi5.jpg')
    
    # accessing all pixel
    px = img[100,100]
    print("print px:%s" %px)
    
    # accessing only blue pixel
    blue = img[100,100,0]
    print("print blue:%s" %blue)
    
    #modify the pixel values and print out result
    img[100,100] = [255,255,255]
    print("print modified pixel:%s" %img[100,100])
    
    #Better pixel accessing and editing method :
    # accessing RED value
    print("accessing RED value:%s" %img.item(10,10,2))
    
    # modifying RED value
    img.itemset((10,10,2),100)
    print("print modified red pixel:%s" %img.item(10,10,2))
    
    #Accessing Image Properties
    print("print img.shape:"+str(img.shape))
    print("print img.size:"+str(img.size))
    print("print img.dtype:"+str(img.dtype))
    
    #Image ROI: copy ball to another region
    ball = img[280:340, 330:390]
    img[273:333, 100:160] = ball
    
    # Display the original frame
    cv2.imshow('Images',img)    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
def MakingBordersImages():
    BLUE = [255,0,0]
    
    img1 = cv2.imread('../../../res/opencv-logo-black.png')
    
    replicate = cv2.copyMakeBorder(img1,10,10,10,10,cv2.BORDER_REPLICATE)
    reflect = cv2.copyMakeBorder(img1,10,10,10,10,cv2.BORDER_REFLECT)
    reflect101 = cv2.copyMakeBorder(img1,10,10,10,10,cv2.BORDER_REFLECT_101)
    wrap = cv2.copyMakeBorder(img1,10,10,10,10,cv2.BORDER_WRAP)
    constant= cv2.copyMakeBorder(img1,10,10,10,10,cv2.BORDER_CONSTANT,value=BLUE)
    
    plt.subplot(231),plt.imshow(img1,'gray')
    plt.title('ORIGINAL'),plt.xticks([]), plt.yticks([])
    plt.subplot(232),plt.imshow(replicate,'gray')
    plt.title('REPLICATE'),  plt.xticks([]), plt.yticks([])
    plt.subplot(233),plt.imshow(reflect,'gray')
    plt.title('REFLECT'),  plt.xticks([]), plt.yticks([])
    plt.subplot(234),plt.imshow(reflect101,'gray')
    plt.title('REFLECT_101'),  plt.xticks([]), plt.yticks([])
    plt.subplot(235),plt.imshow(wrap,'gray')
    plt.title('WRAP'),  plt.xticks([]), plt.yticks([])
    plt.subplot(236),plt.imshow(constant,'gray')
    plt.title('CONSTANT'),  plt.xticks([]), plt.yticks([])
    
    plt.show()

    
if __name__ == '__main__':
    AccessingModifyingpixelvalues()
    MakingBordersImages()
    