
import time
from picamera import PiCamera
from picamera.array import PiRGBArray
import threading
from . import ProcessImage
from . import ProcessImageV1
import multiprocessing
import struct
import queue as Queue

import cv2
import numpy as np

 #   camera.capture_sequence(['image1.jpg','image2.jpg','image3.jpg'],use_video_port=True)

class CameraMgmt(multiprocessing.Process):
    count1=0
    imageCount=0
    hit1 = 0
    latestImage=None
    hit2 = 0
    count2=0
    area1 = 0
    area2 = 0
    x1 = -1
    x2 = -1
    m = multiprocessing.Manager()
    m1 = multiprocessing.Manager()
    m2 = multiprocessing.Manager()
    handle_q = m.Queue()
    process1_q = m1.Queue()
    process2_q = m2.Queue()
    running = False
    def __init__(self,job_q,header):
        multiprocessing.Process.__init__(self)
        self.header = header
        
       
        self.job_q = job_q
        
        print("CameraManager started")
        self.daemon=True
        self.start()

    def run(self):
        self.camera = PiCamera()
        self.rawCapture = PiRGBArray(self.camera)
      
        self.camera.resolution = (480,480)
        self.camera.color_effects = (128,128)
        
        self.camera.exposure_mode = 'antishake'
        self.camera.image_effect = 'denoise'
        #self.camera.metering = 'spot'
        self.camera.framerate=30
        t1 = threading.Thread(target=self.startProcessor1, args=(self.process1_q,))
        t1.start()    
        
        t2 = threading.Thread(target=self.startProcessor2, args=(self.process2_q,))
        t2.start()

        t3 = threading.Thread(target=self.handleProcessor, args=())
        t3.start()

            
        
        t1.join()
        t2.join()
        t3.join()
     
    def startProcessor1(self,image_q):
        self.p = ProcessImage.ProcessImage()
        while True:
            if(image_q.qsize()!=0):
                
                res = (self.p.processImage(image_q.get(),False))#might want to use dict, coordinate as key, arrow found as value
#                self.job_q.put("B:"+str(res))
                 
                print("not mine",res)
                if res[0] != -1:
                   self.hit1 = self.hit1+1
                   self.area1 = res[2]
                   self.x1 = res[1]
                image_q.task_done()
                self.count1 = self.count1+1
            
            time.sleep(0.0001)
    def startProcessor2(self,image_q):
        self.p2 = ProcessImageV1.ProcessImageV1()
        while True:
            if(image_q.qsize()!=0):
                
                res = (self.p2.processImage(image_q.get(),False))#might want to use dict, coordinate as key, arrow found as value
 #               self.job_q.put("B:"+str(res))
                if res != None:
                   if res[0] != -1:
                      self.hit2 = self.hit2+1
                      self.area2 = res[2]
                      self.x2 = res[1]
                   print("mine",res)
                else:
                   print("mineRESNONE",res)
                image_q.task_done()
                self.count2 = self.count2+1
            time.sleep(0.0001)
        
    def getPacketHeader(self):
        return self.header
    
    def captureImage(self):
        if self.running == True:
            pass
        if self.running == False:
            self.running = True
         #do timing here
        image = None
        start = time.time()
        ori_start = start
        i = 0
        for frame in self.camera.capture_continuous(self.rawCapture, format = "rgb",use_video_port=True):
            image = frame.array
            self.process1_q.put(image)
            self.process2_q.put(image)
            self.latestImage = image

            self.rawCapture.truncate(0)
            i = i+1
            if(i==2):
                break   
  
        
        

        end = time.time()
        print("total",end-ori_start)
        
    def handleProcessor(self):
        while True:
            if(self.handle_q.qsize()!=0):
                packet = self.handle_q.get()
                self.handle_q.task_done()
                print("Camera is handling : "+packet+"   \n")
                self.captureImage()
            if (self.count1+self.count2)>=4:
                self.count1 = 0
                self.count2 = 0
                hitRate = (self.hit1+self.hit2)/4.0
                print("HitRate:"+str(hitRate))
                self.hit1 = 0
                self.hit2 = 0

                
                if (hitRate>=0.25):
                    self.imageCount+=1
                    cv2.imwrite(str(self.imageCount)+"HitRate"+str((hitRate*100))+"a1"+str(self.area1)+"a2"+str(self.area2)+"x1"+str(self.x1)+"x2"+str(self.x2)+".png",self.latestImage)
                    if (self.area1 > 16000 or self.area2 > 16000 ):
                        print("arrow=>1")
                        if(self.x1 > 90 or self.x2 > 90): 
                            self.job_q.put(self.header+":B:map:arrow:1:1")
                    elif (self.area1 > 5000 or self.area2>5000):
                        print("arrow=>2")
                        if(self.x1>170 or self.x2 >170):
                            self.job_q.put(self.header+":B:map:arrow:2:1")
                    elif (self.area1 > 2730 or self.area2>2730):
                        print("arrow=>3")
                        if(self.x1 >290 or self.x2 > 290):
                            self.job_q.put(self.header+":B:map:arrow:3:2")
                        elif(self.x1>120 or self.x2>120):
                            self.job_q.put(self.header+":B:map:arrow:3:1")
                    elif (self.area1 > 1600 or self.area2 > 1600):
                        print("arrow=>4")
                        if(self.x1<290 or self.x2<290):
                            if(self.x1>195 or self.x2>195):
                                self.job_q.put(self.header+":B:map:arrow:4:1")
                            elif(self.x1>50 or self.x2>50):
                                self.job_q.put(self.header+":B:map:arrow:4:2")
                            elif(self.x1>25 or self.x2>25):
                                self.job_q.put(self.header+":B:map:arrow:4:3")
                            
                
                self.area1 = 0
                self.x1 = -1
                self.x2 = -1
                self.area2 = 0
            time.sleep(0.001)

    def handle(self,packet):
        self.handle_q.put(packet)
        #self.handle_q.put(self.header + ":B:" + packet)
