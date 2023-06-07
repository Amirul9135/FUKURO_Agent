from datetime import datetime
import json

class CPUReading:
    def __init__(self,reading1,reading2,timeStamp): 
        self._timeStamp = timeStamp.strftime("%Y-%m-%d %H:%M:%S")
        
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
                         
        print(f"Reading 1 {r1}")
        print(f"Reading 2 {r2}")
        print(totalTimeDiff)
        
        #calculate the usage %       
        self._usageTotal = (totalTimeDiff - ((r2[3] + r2[4]) - (r1[3] + r1[4]))) / totalTimeDiff
        self._usageOnUser = ((r2[0] + r2[1]) - (r1[0]+r1[1])) / totalTimeDiff
        self._usageOnSys = (r2[2] - r1[2]) / totalTimeDiff
        self._usageOnInterrupt = ((r2[5] + r2[6]) - (r1[5] + r1[6])) / totalTimeDiff
        
        self._usageTotal = round(self._usageTotal * 100, 2)
        self._usageOnUser = round(self._usageOnUser * 100, 2)
        self._usageOnSys = round(self._usageOnSys * 100, 2)
        self._usageOnInterrupt = round(self._usageOnInterrupt * 100,2)
        
        #assign the cpu name
        self._cpuName = reading2.split()[0]
        
        
        
    
    @staticmethod
    def getCurrent():
        strCPULines = []
        curTime = datetime.now()
        
        #open and read /proc/stat return line that concerns cpu only
        with open('/proc/stat', 'r') as stat_file:
            for line in stat_file:
                if line.startswith('cpu'):
                    strCPULines.append(line)
        return strCPULines, curTime
     
    def getUsageOnUserProcess(self):
        return self._usageOnUser
     
    def getUsageOnSystemProcess(self):
        return self._usageOnSys
    
    def getTotalUsage(self):
        return self._usageTotal
    
    def getReadingTime(self):
        return self._timeStamp
    
    def getCpuName(self):
        return self._cpuName
    
    def getJSON(self):
        return {
            "dateTime": self._timeStamp, 
            "label": self._cpuName,
            "system": self._usageOnSys,
            "user": self._usageOnUser,
            "interrupt": self._usageOnInterrupt,
            "total": self._usageTotal
        }
        
    