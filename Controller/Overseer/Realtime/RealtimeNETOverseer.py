from Controller.Overseer.Abstract.RealtimeMetricOverseer import RealtimeMetricOverseer 
from Controller.WsClient import WsClient 
from Model.NETReading import NETReading
import time

class RealtimeNETOverseer(RealtimeMetricOverseer):
    
    def __init__(self, wsc: WsClient, payload: dict,interval = None, threshold = None, thresholdTick = None, alertCooldown = None):
        
        super().__init__(wsc, payload,interval,threshold,thresholdTick,alertCooldown) 
        wsc.addListener("interval/realtime/net", self.updateInterval)  
        wsc.addListener("toggle/realtime/net", lambda val: self.start() if val else self.stop())
        
    
    def _metricExtraction(self): 
        #Extract 2 reading at 1 sec interval timepoint' 
        reading1, _ = NETReading.readCurrentProc() 
        time.sleep(1)
        reading2, timestamp = NETReading.readCurrentProc()
        
        metric = NETReading(reading1,reading2,timestamp)
        
        #add reading to payload'
        self._transmitReading(NETReading.metricLabel(),metric.toJSON()) 