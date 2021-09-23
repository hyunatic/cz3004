import multiprocessing
import logging
from Networking import SocketServer
from Android import BluetoothMgmt
from Networking import PacketHandler
from Camera import CameraMgmt
from RemoteControlCar import RCMgmt
import time
import queue as Queue

#Create Process Array
processes = []
#Create multi-thread process queue
process_Queue = multiprocessing.Manager().Queue()

#Create Log for Debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',filename="DebugLog.txt",level=logging.DEBUG)

# #Server Details
ip_Address = '192.168.4.4'
port_Number = 5000
server = SocketServer.SocketServer(ip_Address,port_Number,process_Queue,"ALG")

#Create BlueToothManager Thread for Andriod Tablet Connection
bluetoothMgmt = BluetoothMgmt.BluetoothMgmt(1,process_Queue,"AND")

#Create RCMgmt Thread for Remote Control Car Connection Via Serial Port
rcCar = RCMgmt.RCMgmt('/dev/ttyUSB0',115200,0,process_Queue,"STM")

#Create Camera Thread for PI Camera Connection
piCamera = CameraMgmt.CameraMgmt(process_Queue,"IMG");

#Create Packet Handler to identify different services in queue
packetHandler = PacketHandler.PacketHandler()
packetHandler.registerHandler(server)
packetHandler.registerHandler(bluetoothMgmt)
packetHandler.registerHandler(rcCar)
packetHandler.registerHandler(piCamera)


#Adding Services into Process Queue
processes.append(server)
processes.append(bluetoothMgmt)
processes.append(rcCar)
processes.append(piCamera)


while True:
    time.sleep(0.001)
    if(process_Queue.qsize()!=0):
        packetHandler.handle(process_Queue.get())
        process_Queue.task_done()

# Block until all task are done
for t in processes:
    t.join()
print ('All process ended successfully')
