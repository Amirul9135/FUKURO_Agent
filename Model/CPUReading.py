from datetime import datetime 
import json

class CPUReading:
    def __init__(self,reading1,reading2,timeStamp): 
        
        self.__timeStamp = timeStamp.strftime("%Y-%m-%d_%H:%M:%S")
        
        #split the reading line into fields skip 1st field since its a name
        #by index field will contain
        # 0[userprocess], 1[niceduserprocess],2[systemtprocess]
        # 3[idle], 4[iowait], 5[irq], 6[softirq]
        # r1,r2 stands for reading 1 and reading 2
        
        r1 = list(map(int, reading1.split()[1:])) 
        r2 = list(map(int, reading2.split()[1:]))
        
        #total different of time cpu spent on each field
        totalTimeDiff = (r2[0] + r2[1] + r2[2] + r2[3] + r2[4] +
                                    r2[5] + r2[6] ) - (r1[0] + r1[1] 
                                                       + r1[2] + r1[3] + r1[4] + r1[5] + r1[6] ) 
        
        #calculate the usage %        
        self.__usageOnUser = ((r2[0] + r2[1]) - (r1[0]+r1[1])) / totalTimeDiff
        self.__usageOnSys = (r2[2] - r1[2]) / totalTimeDiff
        self.__usageOnInterrupt = ((r2[5] + r2[6]) - (r1[5] + r1[6])) / totalTimeDiff
         
        self.__usageOnUser = round(self.__usageOnUser * 100, 2)
        self.__usageOnSys = round(self.__usageOnSys * 100, 2)
        self.__usageOnInterrupt = round(self.__usageOnInterrupt * 100,2)
        self.__total = self.__usageOnUser + self.__usageOnSys + self.__usageOnInterrupt 
        
    def toJSON(self):
        #convert to json format complies with database entity
        return {
            "dateTime": self.__timeStamp,  
            "system": self.__usageOnSys,
            "user": self.__usageOnUser,
            "interrupt": self.__usageOnInterrupt 
        } 
        
    
    @staticmethod
    def readCurrentProc(): 
        with open('/proc/stat', 'r') as stat_file:
            timestamp = datetime.now()
            for line in stat_file:
                if line.startswith('cpu') and not line[3].isdigit(): #exclude that have digit to only extract total of all core 
                    return line,timestamp
        return 
    
    @staticmethod
    def metricLabel():
        return "cpu"
     
    def getUsageOnUserProcess(self):
        return self.__usageOnUser
     
    def getUsageOnSystemProcess(self):
        return self.__usageOnSys
     
    def getUsageOnInterrupt(self):
        return self.__usageOnInterrupt
    
    def getReadingTime(self):
        return self.__timeStamp
    
    def getTotal(self):
        return self.__total
        
    