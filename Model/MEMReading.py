from datetime import datetime
import subprocess

import pytz

class MEMReading: 
    def __init__(self): 
        values = {
            "MemTotal":0,
            "MemFree":0,
            "Buffers":0,
            "Cached":0,
            "SReclaimable":0
        }
        self.__timeStamp = datetime.isoformat(datetime.now(pytz.utc))
        with open('/proc/meminfo', 'r') as meminfo_file:
            for line in meminfo_file:
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip()
                    value_str = parts[1].strip()
                    if key in values:
                        try:
                            value = int(value_str.split()[0])
                        except ValueError:
                            value = value_str
                        values[key] = value
        self.__total:int  = values["MemTotal"]
        
        #% of memory used for something includeing buffer and cache
        self.__used:float = round( (values["MemTotal"] - values["MemFree"] ) / values["MemTotal"] * 100,2)
        
        #% of the total used as cache
        self.__cached:float =  round( (values["Cached"] - values["SReclaimable"] ) / values["MemTotal"] * 100,2)
        #% of the total used as buffer
        self.__buffer:float =  round( (values["Buffers"] ) / values["MemTotal"] * 100,2) 
    
    def toJSON(self):
        return{
            "dateTime": self.__timeStamp,
            "total": self.__total,
            "used": self.__used,
            "cached": self.__cached,
            "buffer": self.__buffer
        }
    def getUsage(self):
        return self.__used
    
    @staticmethod
    def metricLabel():
        return "mem"
    
    @staticmethod
    def topUsage(limit):
        ''
        ps = []
        limit = limit + 1
        command = "ps -aux --sort -pmem | head -" + str(limit)
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        lines = output.split('\n')
        first = True
        for line in lines:
            if first:
                first = False
            else:
                part = line.split() 
                if(len(part)> 10): 
                    ps.append({
                        "user":part[0],
                        "pid":part[1],
                        "usage":part[3],
                        "command":part[10]
                    })
        return ps

 