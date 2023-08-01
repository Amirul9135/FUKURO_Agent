from ResourceOverseer import ResourceOverseer
from ..Model.MetricsPayload import MetricsPayload
from ..Model.CPUReading import CPUReading
import time

class CPUOverseer(ResourceOverseer):
    def __init__(self,payload:MetricsPayload, intervalExt:int, intervalRT:int):
        
        'minus 1 since cpu extraction itself takes 1 second to extract'
        intervalExt = intervalExt - 1
        super().__init__(payload,intervalExt,intervalRT)
    
    def _extractTask(self):
        
        'Extract 2 reading at 1 sec interval timepoint' 
        reading1,_ = CPUReading.getCurrent() 
        time.sleep(1)
        reading2, timestamp = CPUReading.getCurrent()
        
        'calculate the readings using CPUReading constructor'
        cpuMetric = CPUReading(reading1, reading2, timestamp)
         
        super()._payloadRef.addCPU(cpuMetric.getJSON())
        
        
        
        
    def _extractRTTask(self):
        ''
    