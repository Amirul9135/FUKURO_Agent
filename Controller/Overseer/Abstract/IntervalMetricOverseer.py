from Controller.WsClient import WsClient
from Controller.Overseer.Abstract.MetricOverseer import MetricOverseer 
from Controller.Overseer.Abstract.Threshold import Threshold
import json

class IntervalMetricOverseer(MetricOverseer):
    
    def __init__(self, wsc: WsClient, payload:dict,interval = None, threshold = None, thresholdTick = None, alertCooldown = None):
        super().__init__(wsc,interval)
        
        #payload reference to be populated with the reading values'
        #the structure of payload should be list of strings "cpu":["",""],...'
        self.__payloadRef : dict = payload
         
        self.__threshold = Threshold(self._sendMessage,60,1)
        
    def updateThreshold(self,val):
        self.__threshold.updateThresholds(val)
    
    def updateThresholdDuration(self,val:int):
        self.__threshold.updateTick(val)
        
    def updateAlertCooldown(self,val:int):
        self.__threshold.updateCooldown(val)
    
    def _addReading(self,key:str ,reading:str):
        #append reading in string into the payload list' 
        with self._getThreadLock():
            if not key in self.__payloadRef:
                self.__payloadRef[key] = []
                
            self.__payloadRef[key].append(reading)  
        
    def _triggerAlert(self,value,label:str,reading:dict):
        
        try:
            
            self.__threshold.evaluate(value,{
                        "path":"alert/" + label,
                        "data": reading
                    }) 
        except Exception as e:
            print('trigger alert failed',e)
    def stop(self):
        self.__threshold.stopAll()
        super().stop()
     
   
            
        
        
            
        