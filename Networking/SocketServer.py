import socket 
import time
#from thread import *
import threading
import multiprocessing
import logging
import queue as Queue

class SocketServer(multiprocessing.Process):
    print_lock = threading.Lock()
    handle_q = multiprocessing.Manager().Queue()

    def __init__(self,host,port,job_q,header):
        multiprocessing.Process.__init__(self)
        self.port = port
        self.header=header
        self.logger = logging.getLogger(self.__class__.__name__)
        self.host = host
        self.job_q = job_q
        self.c = None 
        self.daemon=True
        self.start()

    def run(self):
        t2 = threading.Thread(target=self.handleProcessor, args=(0.00001,))
        t2.start()
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)
        while True: 
            print("[LOG][PC]","Listening for connection")
            # Create connection with client 
            self.c, addr = s.accept() 
            
            # Lock acquired by client 
            self.print_lock.acquire() 
            print("[LOG][PC]","Connection from:" + str(addr[0]) +":"+ str(addr[1])) 
            self.job_q.put(self.header+":B:PC Connected") 
 
            t1 = threading.Thread(target=self.thread_receive,args=(self.c,self.job_q,))
            
            t1.start()
            t1.join()
            
       
        s.close()
        t2.join() 

    def getPacketHeader(self):
        return self.header


    def handleProcessor(self,delay):
        while True:
            if(self.handle_q.qsize()!=0):
                packet = self.handle_q.get()
                self.handle_q.task_done()
                splitData = packet.split(':')
                if splitData[1] == "set":
                    if splitData[2] == "startposition":
                        self.job_q.put(self.header+":A:set:startposition:"+splitData[3]+":"+splitData[4])
                        
                self.send_socket(str(packet+"\n"))
            

            time.sleep(delay)

    def handle(self,packet):
        self.handle_q.put(packet)

    def send_socket(self,message):
        try:
                
                if(self.c == None):
                    print("[ERR][PC]","Trying to send but no clients connected")
                    self.job_q.put(self.header+":B:PC not connected")
                else:
                    self.c.sendall(message)
        except socket.error as e:
                print(socket.error)
                self.logger.debug(e)
                
        
# Thread Function
    def thread_receive(self,c,job_q): 
        while True: 
            try:
                data = c.recv(1024)
                data = data.strip().decode('utf-8')
                
                if not data: 
                    print('Bye')
                    self.print_lock.release()    # lock released on exit 
                    break
                    
                if len(data)>0:
                    packets = data.split('$')
                    for line in packets:
                        packet = line           
                        job_q.put(self.header+":"+packet)  
             
                    
            except socket.error as e:
                print(socket.error)
                self.logger.debug(e)
                self.print_lock.release() 
                break
            time.sleep(0.0001)
            
      
            
      
        # Close Connection
        c.close() 
      
        


