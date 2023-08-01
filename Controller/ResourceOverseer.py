from abc import ABC, abstractmethod
from ..Model.MetricsPayload import MetricsPayload
import threading
import time

"""
ResourceOverseer is an abstract class
  it defines the generic behaviour of a resource overseer controller class
  the abstract method will be defined in the concrete class
""" 
class ResourceOverseer(ABC):
     
    def __init__(self,payload:MetricsPayload, intervalExt:int, intervalRT:int):
        self._thRealtime : threading.Thread = None
        self._thExtract : threading.Thread = None
        self._thLock : threading.Lock = threading.Lock()
        self._isOverseeing : bool = False
        self._isRTOverseeing : bool = False
        self._intervalExt : int = intervalExt
        self._intervalRT : int = intervalRT
        self._payloadRef : MetricsPayload = payload
    
    'this method execute the thread'
    def start(self):  
        
        if not self._isOverseeing:
            self._isOverseeing = True
            self._thExtract = threading.Thread(target=self._extract)
    
    'this method gracefully end the extraction thread'
    def stop(self):
        
        if self._isOverseeing:
            self._isOverseeing = False
            self._thExtract.join()
    
    'this method set the extraction interval value and restart the extraction thread'
    def updateExtractInterval(self,val):
        
        self.stop()
        self._intervalExt = val
        self.start()
    
    
    'is a method to be executed in its own thread continuosly'
    def _extract(self):
         
        while self._isOverseeing: 
            
            'call the metric extraction task'
            self._extractTask()
            
            'interval mechanism'
            with self._thLock:
                'copy value of interval to a temporary variable'
                tmpInterval = self._intervalExt
            
            'loop and pause every 1 second' 
            'if the isOverseeing is turned false loop will exit in 1 second to end the thread almost immediately'
            while self._isOverseeing and tmpInterval > 0:
                time.sleep(1)
                tmpInterval -= 1
            
            
    'this method start realtime monitoring on its own thread'
    def startRT(self,wsc):
        
        if not self._isRTOverseeing:
            self._isRTOverseeing = True
            self._thRealtime = threading.Thread(target=self._extractRT)
    
    'this method gracefully ends the realtime monitoring thread'
    def stopRT(self):
        if self._isRTOverseeing:
            self._isRTOverseeing = False
            self._thRealtime.join()
        
    'this method set a new value to the reatime extract interval and restart the threads'    
    def updateRTInterval(self,val):
        self.stopRT()
        self._intervalRT = val
        self.startRT()
    
    'this method continuosly extract metric for realtime use'
    def _extractRT(self): 
        while self._isRTOverseeing: 
            
            'call the realtime metric extraction task'
            self._extractRTTask()
            
            'interval mechanism'
            with self._thLock:
                'copy value of interval to a temporary variable'
                tmpInterval = self._intervalRT
            
            'loop and pause every 1 second' 
            'if the isOverseeing is turned false loop will exit in 1 second to end the thread almost immediately'
            while self._isRTOverseeing and tmpInterval > 0:
                time.sleep(1)
                tmpInterval -= 1
    
    @abstractmethod
    def _extractTask(self):
        pass
    
    @abstractmethod
    def _extractRTTask(self):
        pass
        
    
        
        
        