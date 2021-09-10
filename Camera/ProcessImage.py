
import numpy as np
import cv2
import imutils

class ProcessImage:
    pool = ["Up.png","Down.png","Up1.jpg","Down1.jpg"]
    name = ["Up","Down","Up","Down"]
    image_pool = []
    mult=1.5
    success=0
    def __init__(self):
        #print("ProcessImage started")
        for x in self.pool:
            im = cv2.imread(x)
            self.image_pool.append(im)
        
        

    def convertToBW(self,bw,threshold):
        bw[bw < threshold] = 0    # Black
        bw[bw >= threshold] = 255 # White
        return bw

    def retrieveContours(self, size, image):
        cnts = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:size]
        return cnts

    def getApprox(self, err, contour):
        #always search for closed
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, err * peri, True)
        return len(approx)

    def getEdgedPic(self, image, low, high):
        #Extract edges
        kernel = np.ones((2,2), np.uint8)
        gray_pic = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
#        gray_pic = cv2.GaussianBlur(gray_pic,(3,3),200)   
        edged_pic = cv2.Canny(gray_pic, low, high)
#        edged_pic = cv2.dilate(edged_pic,kernel,iterations=2)
 #       edged_pic = cv2.erode(edged_pic,kernel,iterations=2)
        #edged_pic = cv2.morphologyEx(edged_pic, cv2.MORPH_CLOSE,kernel)
        
        
        return edged_pic

    def calculateBWRatio(self,image):
        #Simple calculation of image's black and white ratio
        n_white_pix = np.sum(image==255)
        n_black_pix = np.sum(image==0)
        
        #to handle div by zero error
        if(n_black_pix==0):
            return 0
        
        ratio = float(n_white_pix)/float(n_black_pix)
        return ratio
    
    def mse(self,imageA, imageB):
        # the 'Mean Squared Error' between the two images is the
        # sum of the squared difference between the two images;
        # NOTE: the two images must have the same dimension
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])
        
        # return the MSE, the lower the error, the more "similar"
        # the two images are
        return err


    def compareWithPool(self,start,end,image,dim):
        #This function will compare the cropped image(input) with the
        #pool of original images.
        #Upon finish comparing, it will return the lowest difference
        #as well as the image pool's index
            
        i = start
        temp = []
        diff = -1
        index = -1
        while(i<=end):
                original = cv2.resize(self.image_pool[i], dim, interpolation = cv2.INTER_AREA)
                original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
                m = self.mse(original, image)
                temp.append(m)
                i = i + 1
                
        diff = max(temp) - min(temp)
        index = temp.index(min(temp))
        return diff,index
    
    def predictArrow(self,image,dim):
        #This function will return the difference(mse) between the original image
        #and the cropped image together with the index
        diff_A,smallest_Ai = self.compareWithPool(0,1,image,dim)
        diff_B,smallest_Bi = self.compareWithPool(2,3,image,dim)
        diff = max(diff_A,diff_B)

        if(diff_A<diff_B):
           smallest_i = smallest_Bi
        else:
           smallest_i = smallest_Ai
      
        return diff,str(self.name[smallest_i]+" arrow")
        
    def showBoundingRect(self,image,corn,rect,text,area):
        #This function will just draw rectangle and overlay text base in inputs
        offset = 0
        x,y,w,h = rect
        if(corn==4):
           if(area<3000):
               offset = area/400
           elif(area>3000 and area<14000 ):
               offset = area/1000
           elif(area>15000 and area <20000):
               offset = area/1800
           else:
               offset = area/2000
        cv2.putText(image, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), lineType=cv2.CV_AA)      
        if corn == 4:     
           cv2.rectangle(image,(x+int(offset),y+int(offset)),(x+w-int(offset),y+h-int(offset)),(0,255,0),1)
        if corn == 7:
           cv2.rectangle(image,(x,y),(x+w,y+h),(33,155,230),1)

    def predictArrow2(self,crop_img,dim):
        original = cv2.resize(self.image_pool[0], dim, interpolation = cv2.INTER_AREA)
        original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        m1 = self.mse(original, crop_img)
        
        original = cv2.resize(self.image_pool[2], dim, interpolation = cv2.INTER_AREA)
        original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        m2 = self.mse(original, crop_img)
        return max(m1,m2)
                           
    def processImage(self,image,show_rect):
        #Backup the original image first
        original = image.copy()
       
        self.succes = -1
        #Convert the image to edged format and find contours
        img = self.getEdgedPic(image.copy(),100,150) #100,150
        #cv2.imwrite("Edged.png",img)        
        cnts = self.retrieveContours(10,img)
        count = 0
        #Look through each contour to perform further processing
        for c in cnts:
            #0.15 == 15% error rate in the shape
            corn = self.getApprox(0.05,c)
           
#            print(corn)
            #We want to detect either arrow(7 corners) or square(4 corners)
            if((corn>=7 and corn<=9) or corn==4):
                area = cv2.contourArea(c)
                #print("PROCESSIMAGE "+str(area))
                #False positive check
                #Checking if the area is above threshold value
                #Some small objects can have 4 or 7 corners too
                if(area>300):#1000
                    #Crop out the image that in this current contour (c)
                    #Convert to black and white so that we can have a better
                    #mean square error matching
                    x,y,w,h = cv2.boundingRect(c)
                    crop_img = image[y:y+h, x:x+w]
                   # cv2.drawContours(image,cnts,-1,(255,0,0),1)
                   # cv2.imshow("AASD",image)
                    crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
                    crop_img = self.convertToBW(crop_img,70)
                   # cv2.imwrite("Cropped.png",crop_img)
                    #cv2.imshow("AASD",crop_img)
                    
                    ratio_bw = self.calculateBWRatio(crop_img)
                   
                    
                    #To get rid of division by zero error
                    #Not sure if it is possible to get height = 0
                    #But no harm adding an if-statement to check
                    if(h == 0):
                        continue
                
                    #False positive check
                    #Check dimension ratio
                    #Image should have a ratio close to 1 since it is square-liked
                    ratio_dim = float(w)/float(h)
                    if(ratio_dim>1.2):
                        #print("R")
                        continue
                    #False positive check
                    #Check black and white ratio
                    #Just in case detected a square but it doesn't contain any black/white
                    if(ratio_bw>1.5):
                        continue
                    mse_ = self.predictArrow2(crop_img,(w,h))
                    #print("MSE",mse_)
                    if mse_ <16000:
                        #print("UPPPPPP",x)
                        return ("Up arrow",x,area,corn)
                    
##                    diff,arrow = self.predictArrow(crop_img,(w,h))
##                    print(diff,arrow)
##                    #The difference must be above the threshold value to be valid
##                    if(diff > 3000 and arrow=="Up arrow"):
##                            rect = (x,y,w,h)
##                            #print("@@@",arrow,rect[0])
##                           # self. success = 1
##                            return arrow,x
##                            if(show_rect==True):
##                                    self.showBoundingRect(original,corn,rect,arrow,area)
##                                    return arrow
                                     
        return -1,-1,-1              
       
        
        
        
