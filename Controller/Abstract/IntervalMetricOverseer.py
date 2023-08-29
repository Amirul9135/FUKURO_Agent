from Controller.WsClient import WsClient
from Controller.Abstract.MetricOverseer import MetricOverseer 
import time
import threading
import json

class IntervalMetricOverseer(MetricOverseer):
    
    def __init__(self, wsc: WsClient, payload:dict,interval = None, threshold = None, thresholdTick = None, alertCooldown = None):
        super().__init__(wsc,interval)
        
        #payload reference to be populated with the reading values'
        #the structure of payload should be list of strings "cpu":["",""],...'
        self.__payloadRef : dict = payload
        
        #the value of critical threshold value which will trigger alerts'
        #default is 101, since reading are in percentage 101 will never be reached signifying disabled alert'
        self.__threshold : int = threshold if threshold is not None else 50
        
        #the number of time reading should hit the threshold consecutively before alert is triggered'
        self.__thresholdTick : int = thresholdTick if thresholdTick is not None else 1
        
        #counter to be used to count how many time readings reached threshold so far'
        self.__thresholdCurrentTick:int = 0
        
        #the duration of cooldown for generating alert in seconds'
        self.__alertCooldown:int = alertCooldown if alertCooldown is not None else 600
        
        #the flag variable to signify cooldown status'
        self.__isAlertOnCooldown :bool = False
        
        #thread which the cooldown process execute on'
        self.__cooldownThread:threading.Thread = None
        
    def updateThreshold(self,val:int):
        if self.__threshold == val :
            return
        with self._getThreadLock():
            self.__threshold = val
    
    def updateThresholdDuration(self,val:int):
        if self.__thresholdTick == val:
            return
        with self._getThreadLock():
            self.__thresholdTick = val
        
    def updateAlertCooldown(self,val:int):
        if self.__alertCooldown == val:
            return
        
        self.__resetAlert()
        self._resetTick()
        self.__alertCooldown = val
    
    def _addReading(self,key:str ,reading:str):
        #append reading in string into the payload list' 
        with self._getThreadLock():
            if not key in self.__payloadRef:
                self.__payloadRef[key] = []
                
            self.__payloadRef[key].append(reading)  
        
    def _triggerAlert(self,label:str,reading:dict):
        #check if alert is on cooldown' 
        with self._getThreadLock():
            isCooldown = self.__isAlertOnCooldown
        if not isCooldown: 
            #increase tick and trigger when reached the tick required'
            self.__thresholdCurrentTick += 1
            print(self.__thresholdCurrentTick)
            if self.__thresholdCurrentTick >= self.__thresholdTick:
                payload = {
                    "path":"alert/" + label,
                    "data": reading
                }
                self._sendMessage(json.dumps(payload).replace('_',' '))
                self.__startAlertCooldown()
    
    def _resetTick(self):
        self.__thresholdCurrentTick = 0
        
    def _getThresholdValue(self):
        with self._getThreadLock():
            return self.__threshold
        
    def __resetAlert(self):
        #make cooldown false'
        with self._getThreadLock():
            if self.__isAlertOnCooldown:
                self.__isAlertOnCooldown = False
        #join thread'
        if self.__cooldownThread is not None:
            self.__cooldownThread.join() 
            
      
    #starts the cooldown on its own thread'
    def __startAlertCooldown(self):  
        
        if not self.__isAlertOnCooldown:
            self.__isAlertOnCooldown = True
        self.__cooldownThread = threading.Thread(target=self.__alertCooldownProcess).start()
    
    #alert cooldown process and counting'
    def __alertCooldownProcess(self):
        cooldown = 0
        #load cooldown duration'
        with self._getThreadLock():
            cooldown = self.__alertCooldown
            
        #loop as long as is cooling down checking both flag and count'
        while self.__isAlertOnCooldown and cooldown > 0:
            cooldown -= 1
            time.sleep(1)
        
        #update cooldown status'
        with self._getThreadLock():
            self.__isAlertOnCooldown = False
        
            
        
        
            
        