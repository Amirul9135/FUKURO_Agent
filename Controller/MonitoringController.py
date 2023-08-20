from Controller.WsClient import WsClient
from Controller.CPUOverseer import CPUOverseer
from Controller.RealtimeCPUOverseer import RealtimeCPUOverseer 
from Controller.Abstract.IntervalMetricOverseer import IntervalMetricOverseer 
import threading
import time
import math 
import re
import json

class MonitoringController:
    
    def __init__(self,wsc:WsClient):
        self.__wsc:WsClient = wsc
        
        #"key":"Overseer"'
        self.__intervalOverseer:dict = {} 
        self.__realtimeOverseer:dict = {}
        
        self.__payload:dict = {}
        self.__pushInterval:int = 15 
        self.__thread:threading.Thread = None
        self.__lock:threading.Lock = threading.Lock()
        self.__isPushing:bool = False
        
        #bind web socket listeners'
        wsc.addListener("interval/push", self.updatePushInterval)
        wsc.addListener("toggle/push", self.toggleIntervalMonitoring)  
        self.setup()
        print("Starting monitoring")
                
    def setup(self):
        #request configs from server db and start/stop/initialize only necessaries'
        self.__intervalOverseer['cpu'] = CPUOverseer(self.__wsc,self.__payload)
        self.__realtimeOverseer['cpu'] = RealtimeCPUOverseer(self.__wsc,self.__payload)
        self.toggleIntervalMonitoring(True)
        self.toggleRealtimeMonitoring(True)
        print(self.__intervalOverseer)
    
    #true will start/restart, false wil stop'
    def toggleIntervalMonitoring(self,run:bool):  
        
        #stop all interval monitoring and pushing'
        for key in self.__intervalOverseer.keys(): 
            self.__intervalOverseer[key]:IntervalMetricOverseer.stop()
        if self.__isPushing:
            with self.__lock:
                self.__isPushing = False
            self.__thread.join()
        
        #if run is true than re run'
        if run:
            #start all interval monitoring and pushing'
            for key in self.__intervalOverseer.keys(): 
                self.__intervalOverseer[key].start()
            with self.__lock:
                self.__isPushing = True
            self.__thread = threading.Thread(target=self.__pushMetric).start() 
    
        
    #true will start/restart, false wil stop'
    def toggleRealtimeMonitoring(self,run:bool):
        
        #stop all realtime monitoring processes'
        for key in self.__realtimeOverseer.keys(): 
            self.__realtimeOverseer[key].stop() 
        
        #if run true re run processes'
        if run:
            #start all interval monitoring and pushing'
            for key in self.__realtimeOverseer.keys(): 
                self.__realtimeOverseer[key].start()   
        
    def updatePushInterval(self,val:int):
        
        #stop process and perform parameter update' 
        if self.__isPushing:
            with self.__lock:
                self.__isPushing = False
            
        self.__thread.join()
        
        with self.__lock:
            self.__pushInterval = val
         
        self.__thread = threading.Thread(target=self.__pushMetric).start() 
    
    def __pushMetric(self):
        ''
        start_time = 0
        end_time = 0
        while self.__isPushing:
            start_time = time.time() 
            with self.__lock: 
                payload = {
                    "path":"reading",
                    "data": self.__payload.copy()  
                }
                
            with self.__lock: 
                self.__payload.clear()
            print('pm') 
            #minify payload
            payload = re.sub(r"\s+|\n","",json.dumps(payload))
            payload = payload.replace('_',' ')  
            self.__wsc.send(payload)
        
            end_time = time.time()
            with self.__lock:
                tmpInterval = self.__pushInterval
            
            tmpInterval = tmpInterval - math.floor(end_time - start_time)
            
            while self.__isPushing and tmpInterval > 0:
                time.sleep(1)
                tmpInterval -= 1
                
            
            