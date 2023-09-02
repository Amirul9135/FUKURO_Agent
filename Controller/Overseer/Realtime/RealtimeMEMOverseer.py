from Controller.Overseer.Abstract.RealtimeMetricOverseer import RealtimeMetricOverseer 
from Controller.WsClient import WsClient 
from Model.MEMReading import MEMReading
import time

class RealtimeMEMOverseer(RealtimeMetricOverseer):
    
    def __init__(self, wsc: WsClient, payload: dict,interval = None, threshold = None, thresholdTick = None, alertCooldown = None):
        
        super().__init__(wsc, payload,interval,threshold,thresholdTick,alertCooldown) 
        wsc.addListener("interval/realtime/mem", self.updateInterval)  
        wsc.addListener("toggle/realtime/mem", lambda val: self.start() if val else self.stop())
        
    
    def _metricExtraction(self): 
        
        metric = MEMReading()
        
        #add reading to payload'
        self._transmitReading(MEMReading.metricLabel(),metric.toJSON()) 