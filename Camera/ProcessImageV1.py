import cv2
from .helle2 import *
import numpy as np
import imutils
class ProcessImageV1:
    mult=2.5
    kernel = np.ones((2,2), np.uint8)


    def __init__(self):
        print("")



    def applyImageEffects(self,image):
        gray_pic1 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_pic1 = cv2.GaussianBlur(gray_pic1,(3,3),100)

        edged_pic1 = cv2.Canny(gray_pic1, 30, 50)
        edged_pic1 = cv2.dilate(edged_pic1, self.kernel, iterations=2)
        edged_pic1 = cv2.erode(edged_pic1, self.kernel, iterations=2)
        return edged_pic1
    
    def calculateBWRatio(self,image):
        #Simple calculation of image's black and white ratio
        n_white_pix = np.sum(image==255)
        n_black_pix = np.sum(image==0)
        
        #to handle div by zero error
        if(n_black_pix==0):
            return 0
        
        ratio = float(n_white_pix)/float(n_black_pix)
        return ratio
    
    def getApprox(self,err,c):
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, err * peri, True)
        return approx

    def convertToBW(self,bw,threshold):
        bw[bw < threshold] = 0    # Black
        bw[bw >= threshold] = 255 # White
        return bw    

    def retrieveContours(self,image,size):
        cnts = cv2.findContours(image.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:size]
        return cnts
    
    def processImage(self,image,show_rect):
        #Convert the image to edged format and find contours
        img = self.applyImageEffects(image.copy())
        cnts = self.retrieveContours(img,5)

        #Look through each contour to perform further processing
        for c in cnts:
            #0.15 == 15% error rate in the shape
            approx = self.getApprox(0.015,c)
            corn = len(approx)
            area = cv2.contourArea(c)
            if corn ==7 and area > 100:
                screenCnt = approx
                x1,y1,w1,h1 = cv2.boundingRect(c)      
                value_x = []
                value_y = []
                
                ii = 0
                while(ii<len(screenCnt)):
                    value_x.append(screenCnt[ii][0][0])
                    value_y.append(screenCnt[ii][0][1])
                    ii = ii+1

             
                check_x = he.findOrientation(value_x,"x") 
                check_y = he.findOrientation(value_y,"y")
                
                prod = int(check_x) * int(check_y)
                #print(check_x,check_y)
                if(prod < 0):
                    #cnt = cnts[count]
                    #x,y,w,h = cv2.boundingRect(cnt)

                    if(prod == -1):
                        #print("!!",(x1))
                        return("Up1",x1,area)
                       # cv2.putText(display, "Up Arrow", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), lineType=cv2.CV_AA) 
                  
                    return -1,-1,-1
                img_box = image.copy()
                rect = cv2.minAreaRect(c)
                box = cv2.cv.BoxPoints(rect)
                box = np.int0(box)
              
                W = rect[1][0]
                H = rect[1][1]

                Xs = [i[0] for i in box]
                Ys = [i[1] for i in box]
                x1 = min(Xs)
                x2 = max(Xs)
                y1 = min(Ys)
                y2 = max(Ys)
                
                rotated = False
                angle = rect[2]

                if angle < -22.5:
                    angle+=44.5
                    rotated = True

                center = (int((x1+x2)/2), int((y1+y2)/2))
                size = (int(self.mult*(x2-x1)),int(self.mult*(y2-y1)))

                M = cv2.getRotationMatrix2D((size[0]/2, size[1]/2), angle, 1.0)

                cropped = cv2.getRectSubPix(img_box, size, center)    
                cropped = cv2.warpAffine(cropped, M, size)

                croppedW = W if not rotated else H 
                croppedH = H if not rotated else W

                croppedRotated = cv2.getRectSubPix(cropped, (int(croppedW*self.mult), int(croppedH*self.mult)), (size[0]/2, size[1]/2))
                width2 = croppedRotated.shape[1]
                height2 = croppedRotated.shape[0]
                croppedRotated = self.convertToBW(croppedRotated,70)
                #DO FALSE POSITIVE CHECK HERE, BW RATIO will do i think? not sure if dimen ratio will be reliable...
                ratio_bw = self.calculateBWRatio(croppedRotated)

                #To get rid of division by zero error
                #Not sure if it is possible to get height = 0
                #But no harm adding an if-statement to check
                if(height2 == 0):
                    continue
               
                #False positive check
                #Check dimension ratio
                #Image should have a ratio close to 1 since it is square-liked
                ratio_dim = float(width2)/float(height2)
                if(ratio_dim>1.2):
                    continue
                #False positive check
                #Check black and white ratio
                #Just in case detected a square but it doesn't contain any black/white
                if(ratio_bw>1.5):
                    continue

                
                edged_pic1 = self.applyImageEffects(croppedRotated)
               # cv2.imshow("Show Edged", edged_pic1)
                cnts3 = self.retrieveContours(edged_pic1,3)

                screenCnt2 = None
                    
                for c2 in cnts3:
                        approx1 = self.getApprox(0.015,c2)
                        screenCnt2 = approx1
                        area = cv2.contourArea(c2)
                        value_x = []
                        value_y = []
                        
                        ii = 0
                        while(ii<len(screenCnt2)):
                            value_x.append(screenCnt2[ii][0][0])
                            value_y.append(screenCnt2[ii][0][1])
                            ii = ii+1

                     
                        check_x = he.findOrientation(value_x,"x") 
                        check_y = he.findOrientation(value_y,"y")
                        
                        prod = int(check_x) * int(check_y)
                        #print(check_x,check_y)
                        if(prod < 0):
                            #cnt = cnts[count]
                            x,y,w,h = cv2.boundingRect(c2)
        
                            if(prod == -1):return("Up",x1,area)
                               # cv2.putText(display, "Up Arrow", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), lineType=cv2.CV_AA) 
                            elif(prod == -2):return("Down",-1,-1)
                               # cv2.putText(display, "Down Arrow", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), lineType=cv2.CV_AA)                            
                            elif(prod == -3):return("Left",-1,-1)
                               # cv2.putText(display, "Left Arrow", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), lineType=cv2.CV_AA) 
                            elif(prod == -4):return("Right",-1,-1)
                               # cv2.putText(display, "Right Arrow", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), lineType=cv2.CV_AA)
                            #cv2.drawContours(image,cnts,count,(255,0,0),2)
                            #cv2.rectangle(display,(x,y),(x+w,y+h),(0,255,0),1) 
                        return -1,-1,-1
                return -1,-1,-1
                
        
        
        
