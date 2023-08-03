from abc import ABC, abstractmethod 
from Controller.WsClient import WsClient
import threading
import time
import math

class MetricOverseer(ABC):
    ''
    def __init__(self,wsc:WsClient,interval=None):
        'the web socket client object to be used for connection with server application'
        self.__wsc:WsClient = wsc
        
        'the thread that this overseer processes will execute on'
        self.__thread :threading.Thread = None
        
        
        'the flag variable to indicate process status'
        self.__isOverseeing :bool = False
        
        'the interval in second to execute the abstract _metricExtraction method'
        self.__interval :int = interval if interval is not None else 10
        
        'the thread lock to implement thread safe access'
        self.__lock :threading.Lock = threading.Lock()
        
    'this method execute the overseeing functionality on its own thread'
    def start(self):   
        if not self.__isOverseeing: 
            self.__isOverseeing = True
            self.__thread = threading.Thread(target=self.__extractMetric).start()
    
    'this method gracefully stop the overseeing functionility which is running on its own thread'
    def stop(self): 
        if self.__isOverseeing:
            self.__isOverseeing = False
            self.__thread.join()
    
    'update the value of the interval'
    def updateInterval(self,val:int):
        self.stop()
        self.__interval = val
        self.start()
        
    'this method perform the metric extraction task continuosly'    
    def __extractMetric(self):  
        'variable declaration outside loop to reuse memory space and reduce memory allocation overheads'
        tmpInterval = 0 
        start_time = 0
        end_time = 0
         
        while self.__isOverseeing: 
            
            start_time = time.time()
            
            'call the metric extraction task'
            self._metricExtraction()
            
            end_time = time.time()
            
            'interval mechanism'
            with self.__lock:
                'copy value of interval to a temporary variable'
                tmpInterval = self.__interval
            
            'deduct consumed time taken during the extraction process'
            tmpInterval = tmpInterval - math.floor(end_time - start_time)
            
            'loop and pause every 1 second' 
            'if the isOverseeing is turned false loop will exit in 1 second to end the thread almost immediately'
            while self.__isOverseeing and tmpInterval > 0:
                time.sleep(1)
                tmpInterval -= 1
                
                
    'send a string to the web socket server'
    def _sendMessage(self,message:str):
        self.__wsc.send(message)
    
    
    def _getThreadLock(self):
        return self.__lock    
    
    @abstractmethod
    def _metricExtraction(self):
        pass
        