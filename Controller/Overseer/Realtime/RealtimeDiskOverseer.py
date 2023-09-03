from Controller.Overseer.Abstract.RealtimeMetricOverseer import RealtimeMetricOverseer 
from Controller.WsClient import WsClient 
from Model.DiskReading import DiskReading
import time
import copy

class RealtimeDiskOverseer(RealtimeMetricOverseer):
    
    def __init__(self, wsc: WsClient, payload: dict,diskList:dict,interval = None, threshold = None, thresholdTick = None, alertCooldown = None):
        
        super().__init__(wsc, payload,interval,threshold,thresholdTick,alertCooldown) 
        wsc.addListener("interval/realtime/dsk", self.updateInterval)  
        wsc.addListener("toggle/realtime/dsk", lambda val: self.start() if val else self.stop())
        self.__disk = diskList
        
    
    def _metricExtraction(self): 
        #Extract 2 reading at 1 sec interval timepoint' 
        reading1 = copy.deepcopy(self.__disk )
        reading2 = copy.deepcopy(self.__disk ) 
        start_time,_ = DiskReading.readCurrentProc(reading1) 
        time.sleep(1) 
        end_time,t2 = DiskReading.readCurrentProc(reading2)  
        elapsed = (end_time - start_time) * 1000  

        for key in reading2:
            metric = DiskReading(reading1[key]['reading'],reading2[key]['reading'],reading2[key]['sect'],elapsed,t2) 
            self._transmitReading(DiskReading.metricLabel(),metric.toJSON(key)) 
        