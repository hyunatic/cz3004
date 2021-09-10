from bluetooth import *
import threading
import time
import struct
import logging
import json
import multiprocessing
import queue as Queue

class BluetoothMgmt(multiprocessing.Process):
    handle_q = multiprocessing.Manager().Queue()
    whitelist = ['50:50:A4:33:9C:09']
    
  
    def __init__(self,port,job_q,header):
        multiprocessing.Process.__init__(self)

        self.port = port
        self.logger = logging.getLogger(self.__class__.__name__)
        self.c = None
        self.header = header
        self.job_q = job_q
        self.daemon=True
        self.start()


    def recv(self,c):
        while True:
            try:
                data = c.recv(1024)
                if len(data)>0:
                     packet = data
                     self.job_q.put(self.header+":"+packet)   
            except BluetoothError as e:
                print("[ERR][ANDROID]:","Disconnection")#can consider logging...
                self.logger.debug(e)
                
                break
            time.sleep(0.00001)
        self.c.close()
        self.c = None

    def send(self,c,message): 
        if(self.c == None):
            print("[ERR][ANDROID]:","Trying to send but no clients connected")
        else:
            self.c.send(str(message+"\n"))
            time.sleep(0.6)  
        
            

    def close_connection(self,c):
        self.c.close()

    def getPacketHeader(self):
        return self.header
    
    def handleProcessor(self):
        while True:
            if(self.handle_q.qsize()!=0):
                packet = self.handle_q.get()
                self.handle_q.task_done()
                
                self.send(self.c,packet)
                
            time.sleep(0.000001)

    def handle(self,packet):
        self.handle_q.put(packet)
        
    def run(self):
        t2 = threading.Thread(target=self.handleProcessor, args=())
        t2.start()
        
        server_sock=BluetoothSocket( RFCOMM )
        server_sock.bind(("",self.port))
        server_sock.listen(1)
	       
        while True:
            print("[LOG][ANDROID]","Listening for connection")
            self.c,address = server_sock.accept()
            if address[0] in self.whitelist:
                
                print ("[LOG][ANDROID]","Connection from: "+str(address))
                
                t = threading.Thread(target=self.recv,args=(self.c,))
                t.start()
                t.join()
            else :
                print("[ERR][ANDROID]","Unknown device tried to connect. MAC: "+address)
                self.logger.debug("Unknown device tried to connect. MAC:",address)
                self.c.close()
                
           
        self.c.close()
        server_sock.close()
        t2.join()

#b = BluetoothManager(6)
