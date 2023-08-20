from Controller.Abstract.RealtimeMetricOverseer import RealtimeMetricOverseer 
from Controller.WsClient import WsClient 
from Model.CPUReading import CPUReading
import time

class RealtimeCPUOverseer(RealtimeMetricOverseer):
    
    def __init__(self, wsc: WsClient, payload: dict,interval = None, threshold = None, thresholdTick = None, alertCooldown = None):
        
        super().__init__(wsc, payload,interval,threshold,thresholdTick,alertCooldown) 
        wsc.addListener("interval/realtime/cpu", self.updateInterval)  
        wsc.addListener("toggle/realtime/cpu", lambda val: self.start() if val else self.stop())
        
    
    def _metricExtraction(self): 
        #Extract 2 reading at 1 sec interval timepoint' 
        reading1, _ = CPUReading.readCurrentProc() 
        time.sleep(1)
        reading2, timestamp = CPUReading.readCurrentProc()
        
        metric = CPUReading(reading1,reading2,timestamp)
        
        #add reading to payload'
        self._transmitReading(CPUReading.metricLabel(),metric.toJSON()) 