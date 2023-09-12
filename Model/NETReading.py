from datetime import datetime  
import time

import pytz

class NETReading:
    def __init__(self,reading1,reading2,timeStamp): 
        #[94208297, 595019, 0, 0, 0, 0, 0, 0, 57473667, 561279, 0, 0, 0, 0, 0, 0]
        # received [0] byte ;[1] packet ;[ 2] err ;[ 3] drop ;[ 4] fifo ;[ 5] frame ;[ 6] compressed ;[ 7] multicast ;
        # transmit [8] byte ;[9] packet ;[10] err ;[11] drop ;[12] fifo ;[13] colls ;[14] carrier    ;[15] compressed;
        self.__timeStamp =  datetime.isoformat(timeStamp)
        self.__rByte = round((reading2[0] - reading1[0]) / 1024,2)
        self.__tByte = round((reading2[8] - reading1[8]) / 1024,2) 
        self.__rErr = reading2[2] - reading1[2]
        self.__tErr = reading2[10] - reading1[10]
        self.__rDrop = reading2[3] - reading1[3]
        self.__tDrop = reading2[11] - reading1[11]
           
    
    @staticmethod
    def readCurrentProc(): 
        readings = []
        with open('/proc/net/dev', 'r') as lines:  
            timestamp = datetime.now(pytz.utc)
            for line in lines:
                part = line.split()
                try:
                    test = int(part[1])
                    readings.append(list(map(int, part[1:])) )  
                except ValueError:
                    ''
        finalReading = readings[0]
        for i in range(1,len(readings)):
            finalReading = [a1+a2 for a1,a2 in zip(finalReading,readings[i])] 
        return finalReading, timestamp
    
    def getReceived(self):
        return self.__rByte
    def toJSON(self):
        #convert to json format complies with database entity
        return {
            "dateTime": self.__timeStamp,
            "rkByte": self.__rByte, 
            "rError": self.__rErr,
            "rDrop": self.__rDrop,
            "tkByte": self.__tByte, 
            "tError" : self.__tErr,
            "tDrop" : self.__tDrop
        } 
        
    
    @staticmethod
    def metricLabel():
        return "net"
     
 