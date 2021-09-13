import logging
import struct
import os
class PacketHandler:
    
    handlers = {}

    def __init__(self):      
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def measure_temp(self):
        temp = os.popen("vcgencmd measure_temp").readline()
        return (temp.replace("temp=",""))

    def registerHandler(self,instance):
        unique_id = instance.getPacketHeader()
        if unique_id not in self.handlers:
            self.handlers[unique_id] = instance
        else:
            print("Failed to register handler, please choose another unique_id")

    def unregisterHandler(self,unique_id):
        try:
            del self.handlers[unique_id]
        except KeyError:
            print("Fail to remove, handler not found.")

    def convertToName(self,header):
        if header == 'A':
                return "RC-Car"
        elif header == 'B':
                return "ANDROID"
        elif header == 'P':
                return "PC"
        elif header == 'R':
                return "RPI"
            
    def handle(self,packet):
        splitData = packet.split(':')
        if len(splitData)>1:
            print(splitData)
            recv_from = splitData[0]
            
            unique_id = splitData[1]
          
            if unique_id in self.handlers:
                if not packet.startswith("P:A:set:startposition"):
                    lo = ("["+self.measure_temp().strip()+"][MSG]["+self.convertToName(recv_from)+"->"+self.convertToName(unique_id)+"]:",packet[2:])
                    print("Print lo var: " + lo)
                self.handlers[unique_id].handle(packet[2:]+"\n")
        else:
            print("[ERR][PACKETHANDLER]:",packet)
            self.logger.debug("UnknownPacketDestination "+packet)
          
