from Controller.WsClient import WsClient
from Controller.CPUOverseer import CPUOverseer
from Controller.Abstract.IntervalMetricOverseer import IntervalMetricOverseer 
import threading
import time
import math 
import re
import json

class MonitoringController:
    
    def __init__(self,wsc:WsClient):
        self.__wsc:WsClient = wsc
        
        '"key":"Overseer"'
        self.__intervalOverseer:dict = {} 
        self.__realtimeOverseer:dict = {}
        
        self.__payload:dict = {}
        self.__pushInterval:int = 15 
        self.__thread:threading.Thread = None
        self.__lock:threading.Lock = threading.Lock()
        self.__isPushing:bool = False
        
        'bind web socket listeners'
        wsc.addListener("interval/push", self.updatePushInterval)
        wsc.addListener("toggle/push", self.toggleIntervalMonitoring)  
        self.setup()
                
    def setup(self):
        'request configs from server db and start/stop/initialize necessaries'
        self.__intervalOverseer['cpu'] = CPUOverseer(self.__wsc,self.__payload)
        self.toggleIntervalMonitoring(True)
        print(self.__intervalOverseer)
    
    def toggleIntervalMonitoring(self,run:bool): 
        ''
        if run:
            'start all interval monitoring and pushing'
            for key in self.__intervalOverseer.keys(): 
                self.__intervalOverseer[key].start()
            with self.__lock:
                self.__isPushing = True
            self.__thread = threading.Thread(target=self.__pushMetric).start()
        else:
            'stop all interval monitoring and pushing'
            for key in self.__intervalOverseer.keys(): 
                self.__intervalOverseer[key]:IntervalMetricOverseer.stop()
            with self.__lock:
                self.__isPushing = False
            self.__thread.join()
    
        
    def toggleRealtimeMonitoring(self,run:bool):
        ''
        
    def updatePushInterval(self,val:int):
        ''
        with self.__lock:
            self.__pushInterval = val
    
    def __pushMetric(self):
        ''
        start_time = 0
        end_time = 0
        while self.__isPushing:
            start_time = time.time() 
            with self.__lock: 
                payload = {
                    "path":"payload",
                    "data": self.__payload.copy()  
                }
                
            with self.__lock: 
                self.__payload.clear()
            
            #minify payload
            payload = re.sub(r"\s+|\n","",json.dumps(payload))
            payload = payload.replace('_',' ')
            print('payload')
            print(payload)
        
            end_time = time.time()
            with self.__lock:
                tmpInterval = self.__pushInterval
            
            tmpInterval = tmpInterval - math.floor(end_time - start_time)
            
            while self.__isPushing and tmpInterval > 0:
                time.sleep(1)
                tmpInterval -= 1
                
            
            