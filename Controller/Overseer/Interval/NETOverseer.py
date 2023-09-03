from Controller.Overseer.Abstract.IntervalMetricOverseer import IntervalMetricOverseer 
from Controller.WsClient import WsClient 
from Model.NETReading import NETReading
import time

class NETOverseer(IntervalMetricOverseer):
    
    def __init__(self, wsc: WsClient, payload: dict,interval = None, threshold = None, thresholdTick = None, alertCooldown = None):
        super().__init__(wsc, payload,interval,threshold,thresholdTick,alertCooldown) 
        wsc.addListener("interval/net", self.updateInterval)
        wsc.addListener("alert/cooldown/net", self.updateAlertCooldown)
        wsc.addListener("alert/threshold/net",self.updateThreshold)
        wsc.addListener("alert/threshold/tick/net", self.updateThresholdDuration) 
        wsc.addListener("toggle/net", lambda val: self.start() if val else self.stop())
 
    def _metricExtraction(self): 
        #Extract 2 reading at 1 sec interval timepoint' 
        reading1, _ = NETReading.readCurrentProc() 
        time.sleep(1)
        reading2, timestamp = NETReading.readCurrentProc()
        
        metric = NETReading(reading1,reading2,timestamp)
        
        #add reading to payload'
        self._addReading(NETReading.metricLabel(),metric.toJSON()) 
        
        #alert condition and trigger'  
        self._triggerAlert(metric.getReceived(),NETReading.metricLabel(),metric.toJSON()) 
         
        