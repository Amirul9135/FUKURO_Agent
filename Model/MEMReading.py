from datetime import datetime

class MEMReading: 
    def __init__(self): 
        values = {
            "MemTotal":0,
            "MemFree":0,
            "Buffers":0,
            "Cached":0,
            "SReclaimable":0
        }
        self.__timeStamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
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
        self.__used:float = round( (values["MemTotal"] - values["MemFree"] ) / values["MemTotal"] * 100,2)
        self.__cached:float =  round( (values["Cached"] - values["SReclaimable"] ) / values["MemTotal"] * 100,2)
        self.__buffer:float =  round( (values["Buffers"] ) / values["MemTotal"] * 100,2) 
    
    def toJson(self):
        return{
            "dateTime": self.__timeStamp,
            "total": self.__total,
            "used": self.__used,
            "cached": self.__cached,
            "buffer": self.__buffer
        }
    
        