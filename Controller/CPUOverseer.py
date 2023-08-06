from Controller.Abstract.IntervalMetricOverseer import IntervalMetricOverseer 
from Controller.WsClient import WsClient 
from Model.CPUReading import CPUReading
import time

class CPUOverseer(IntervalMetricOverseer):
    
    def __init__(self, wsc: WsClient, payload: dict,interval = None, threshold = None, thresholdTick = None, alertCooldown = None):
        super().__init__(wsc, payload,interval,threshold,thresholdTick,alertCooldown) 
        wsc.addListener("interval/cpu", self.updateInterval)
        wsc.addListener("alert/cooldown/cpu", self.updateAlertCooldown)
        wsc.addListener("alert/threshold/cpu",self.updateThreshold)
        wsc.addListener("alert/threshold/tick/cpu", self.updateThresholdDuration) 
        wsc.addListener("toggle/cpu", lambda val: self.start() if val else self.stop())
 
    def _metricExtraction(self): 
        'Extract 2 reading at 1 sec interval timepoint' 
        reading1, _ = CPUReading.readCurrentProc() 
        time.sleep(1)
        reading2, timestamp = CPUReading.readCurrentProc()
        
        metric = CPUReading(reading1,reading2,timestamp)
        
        'add reading to payload'
        self._addReading(CPUReading.metricLabel(),metric.toJSON()) 
        
        'alert condition and trigger'  
        if metric.getTotal() >= self._getThresholdValue():  
            self._triggerAlert(CPUReading.metricLabel(),metric.toJSON())
        else:
            self._resetTick()
         
        