from Controller.Overseer.Abstract.IntervalMetricOverseer import IntervalMetricOverseer 
from Controller.WsClient import WsClient 
from Model.MEMReading import MEMReading
import time

class MEMOverseer(IntervalMetricOverseer):
    
    def __init__(self, wsc: WsClient, payload: dict,interval = None, threshold = None, thresholdTick = None, alertCooldown = None):
        super().__init__(wsc, payload,interval,threshold,thresholdTick,alertCooldown) 
        wsc.addListener("interval/mem", self.updateInterval)
        wsc.addListener("alert/cooldown/mem", self.updateAlertCooldown)
        wsc.addListener("alert/threshold/mem",self.updateThreshold)
        wsc.addListener("alert/threshold/tick/mem", self.updateThresholdDuration) 
        wsc.addListener("toggle/mem", lambda val: self.start() if val else self.stop())
 
    def _metricExtraction(self): 
        #Extract 2 reading at 1 sec interval timepoint' 
        
        reading = MEMReading() 
        
        #add reading to payload'
        self._addReading(MEMReading.metricLabel(), reading.toJSON()) 
        
        #alert condition and trigger'  
            
        self._triggerAlert(reading.getUsage(),MEMReading.metricLabel(),reading.toJSON()) 
         
        