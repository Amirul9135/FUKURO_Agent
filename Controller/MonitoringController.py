from Controller.WsClient import WsClient


from Controller.Overseer.Interval.CPUOverseer import CPUOverseer
from Controller.Overseer.Interval.MEMOverseer import MEMOverseer


from Controller.Overseer.Realtime.RealtimeCPUOverseer import RealtimeCPUOverseer  
from Controller.Overseer.Realtime.RealtimeMEMOverseer import RealtimeMEMOverseer 


from Controller.Overseer.Abstract.IntervalMetricOverseer import IntervalMetricOverseer 
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
        self.__thread:threading.Thread =  threading.Thread(target=self.__pushMetric)
        self.__lock:threading.Lock = threading.Lock()
        self.__isPushing:bool = False
        
        #bind web socket listeners'
        self.__wsc.addListener("interval/push", self.updatePushInterval)
        self.__wsc.addListener("toggle/push", self.toggleIntervalMonitoring)  
        self.setup()
        print("Starting monitoring")
                
    def setup(self):
        #initialize controllers
        self.__intervalOverseer['cpu'] = CPUOverseer(self.__wsc,self.__payload)
        self.__realtimeOverseer['cpu'] = RealtimeCPUOverseer(self.__wsc,self.__payload) 
        
        self.__intervalOverseer['mem'] = MEMOverseer(self.__wsc,self.__payload)
        self.__realtimeOverseer['mem'] = RealtimeMEMOverseer(self.__wsc,self.__payload) 
        
        
        #request configs from server db and start/stop/initialize only necessaries'
        self.__wsc.send(json.dumps({
                "path":"config"
            }).replace('_',' '))
    
    #true will start/restart, false wil stop'
    def toggleIntervalMonitoring(self,run:bool):  
        
        #stop all interval monitoring and pushing'
        for key in self.__intervalOverseer.keys(): 
            self.__intervalOverseer[key]:IntervalMetricOverseer.stop()
        if self.__isPushing:
            with self.__lock:
                self.__isPushing = False
            if self.__thread.is_alive():
                self.__thread.join()
        
        #if run is true than re run'
        if run:
            #start all interval monitoring and pushing'
            for key in self.__intervalOverseer.keys(): 
                self.__intervalOverseer[key].start()
            with self.__lock:
                self.__isPushing = True 
            self.__thread = threading.Thread(target=self.__pushMetric)
            self.__thread.start()
    
        
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
        if type(val) != int:
            val = int(val) 
        
        
        #if same value no change no need to proceed
        if self.__pushInterval == val:
            print('update cancel, same value')
            return
        
        #stop process and perform parameter update' 
        tmpPush = False
        if self.__isPushing:
            with self.__lock:
                tmpPush = True
                self.__isPushing = False
        if self.__thread.is_alive():
            self.__thread.join()
        
        with self.__lock:
            self.__pushInterval = val 
            self.__isPushing = tmpPush
        self.__thread = threading.Thread(target=self.__pushMetric)
        self.__thread.start() 
    
    def __pushMetric(self):
        ''
        print('push metric')
        start_time = 0
        end_time = 0
        while self.__isPushing:
            
            with self.__lock:
                tmpInterval = self.__pushInterval
            
            tmpInterval = tmpInterval - math.floor(end_time - start_time)
            
            while self.__isPushing and tmpInterval > 0:
                time.sleep(1)
                tmpInterval -= 1
            
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
                
            
            