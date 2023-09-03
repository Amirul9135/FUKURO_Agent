from datetime import datetime
import subprocess
import time
import copy


class DiskReading: 
    
    #@Param, diskNames dict key diskname, value is the columnd readings
    #         reading should be array of the column from diskstat
    # timestamp should be the time of second reading
    # interval should be milisecond interval between first and second reading
    def __init__(self,reading1,reading2,sector,interval,timeStamp): 
        
        self.__timeStamp = timeStamp.strftime("%Y-%m-%d_%H:%M:%S")
         
        self.__usage = round((reading2[10] - reading1[10])/interval * 100,2)
        if self.__usage > 100:
            self.__usage = 100 
            
        #sector bytes to kB, interval mili to second === kb/s
        self.__write = round( (reading2[6] - reading1[6]) * sector /1024 / (interval/1000),2)
        self.__read = round( (reading2[2] - reading1[2]) * sector /1024 / (interval/1000),2) 
        
    def toJSON(self,name):
        #convert to json format complies with database entity
        return {
            "name": name,
            "dateTime": self.__timeStamp,  
            "utilization": self.__usage,
            "writeSpeed": self.__write,
            "readSpeed": self.__read 
        }  
        
    def getUsage(self):
        return self.__usage 
    
    #@Param, diskNames dict key diskname, value is the columnd readings
    #          {"sda1":{'reading':[1,2,3,reading..],'sect':int}}
    #@Return, disct with the diskName as key and
    @staticmethod
    def readCurrentProc(disks): 
        with open('/proc/diskstats', 'r') as stat_file:
            timepoint = time.perf_counter()
            timestamp = datetime.now()
            for line in stat_file:
                part = line.split()
                name = part[2]
                column = list(map(int, part[3:]))  
                if len(column) > 0:
                    if name in disks:
                        disks[name]['reading'] = column 
        return timepoint,timestamp
    
    @staticmethod
    def getSectorSize(disks):
        command = ["lsblk","-l", "-o", "NAME,PHY-SEC"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            output_lines = result.stdout.strip().split('\n') 
            for line in output_lines:
                part = line.split()
                if part[0] in disks:
                    disks[part[0]]['sect'] = int(part[1])

    
    @staticmethod
    def metricLabel():
        return "dsk"
    
    @staticmethod
    def diskStruct(): 
        dsk = {}
        dsk['reading'] = None
        dsk['sect'] = None
        return dsk
    
        
    
"""
reading = {'sda':DiskReading.diskStruct()}
DiskReading.getSectorSize(reading) 

while True:
    reading1 = copy.deepcopy(reading)
    reading2 = copy.deepcopy(reading) 
    start_time,t1 = DiskReading.readCurrentProc(reading1) 
    time.sleep(1) 
    end_time,t2 = DiskReading.readCurrentProc(reading2)  
    elapsed = (end_time - start_time) * 1000  

    for key in reading2:
        metric = DiskReading(reading1[key]['reading'],reading2[key]['reading'],reading2[key]['sect'],elapsed,t2)
    
    """
            
             
            

"""
        0  major number
		1  minor mumber
		2  device name
		3  reads completed successfully
		4  reads merged
		5  sectors read
		6  time spent reading (ms)
		7  writes completed
		8  writes merged
		9  sectors written
		10  time spent writing (ms)
		11  I/Os currently in progress
		12  time spent doing I/Os (ms)
		13  weighted time spent doing I/Os (ms)
		==  =================================== 
		14  discards completed successfully
		15  discards merged
		16  sectors discarded
		17  time spent discarding
		==  =================================== 
		18  flush requests completed successfully
		19  time spent flushing 
""" 