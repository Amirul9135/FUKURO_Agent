from Controller.WsClient import WsClient


from Controller.Overseer.Interval.CPUOverseer import CPUOverseer
from Controller.Overseer.Interval.MEMOverseer import MEMOverseer
from Controller.Overseer.Interval.DiskOverseer import DiskOverseer
from Controller.Overseer.Interval.NETOverseer import NETOverseer


from Controller.Overseer.Realtime.RealtimeCPUOverseer import RealtimeCPUOverseer  
from Controller.Overseer.Realtime.RealtimeMEMOverseer import RealtimeMEMOverseer 
from Controller.Overseer.Realtime.RealtimeDiskOverseer import RealtimeDiskOverseer 
from Controller.Overseer.Realtime.RealtimeNETOverseer import RealtimeNETOverseer 


from Controller.Overseer.Abstract.IntervalMetricOverseer import IntervalMetricOverseer 

from Controller.NodeSpecification import NodeSpecification

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
        
        #for disk list
        self.__disk = {}
        
        #upload specs
         
        self.__wsc.send(json.dumps({ 
            'path': 'post/spec/cpu',
            'data': NodeSpecification.cpu_spec()
            }))
        self.__wsc.send(json.dumps({ 
            'path': 'post/spec/ip',
            'data': NodeSpecification.ip_address()
            }))
        #upload speccs end
        
        self.__refreshDiskSpec()
        self.__wsc.addListener("refresh/disk", self.__refreshDiskSpec)
        
        #bind web socket listeners'
        self.__wsc.addListener("interval/push", self.updatePushInterval)
        self.__wsc.addListener("toggle/push", self.toggleIntervalMonitoring)   
        self.setup() 
        print("Starting monitoring")
    def stopAll(self):
        for overseer in self.__intervalOverseer:
            overseer.stop()
        for rtOv in self.__realtimeOverseer:
            rtOv.stop()
        self.toggleIntervalMonitoring(False) 
         
    def setup(self):
        #initialize controllers
        self.__intervalOverseer['cpu'] = CPUOverseer(self.__wsc,self.__payload)
        self.__realtimeOverseer['cpu'] = RealtimeCPUOverseer(self.__wsc,self.__payload) 
        
        self.__intervalOverseer['mem'] = MEMOverseer(self.__wsc,self.__payload)
        self.__realtimeOverseer['mem'] = RealtimeMEMOverseer(self.__wsc,self.__payload) 
        
        self.__intervalOverseer['dsk'] = DiskOverseer(self.__wsc,self.__payload,self.__disk)
        self.__realtimeOverseer['dsk'] = RealtimeDiskOverseer(self.__wsc,self.__payload,self.__disk) 
        
        self.__intervalOverseer['net'] = NETOverseer(self.__wsc,self.__payload)
        self.__realtimeOverseer['net'] = RealtimeNETOverseer(self.__wsc,self.__payload) 
        
        
        #request configs from server db and start/stop/initialize only necessaries'
        self.__wsc.send(json.dumps({
                "path":"config"
            }))
        self.__wsc.send(json.dumps({ 
            'path': 'get/spec/disk' 
            }))
    
    #true will start/restart, false wil stop'
    def toggleIntervalMonitoring(self,run:bool):  
        
        #stop all interval monitoring and pushing' 
        if self.__isPushing:
            with self.__lock:
                self.__isPushing = False
            if self.__thread.is_alive():
                self.__thread.join()
        
        #if run is true than re run'
        if run: 
            with self.__lock:
                self.__isPushing = True 
            self.__thread = threading.Thread(target=self.__pushMetric)
            self.__thread.start()
    
         
        
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
            #minify payload
            payload = re.sub(r"\s+|\n","",json.dumps(payload)) 
            try:
                self.__wsc.send(payload)
                with self.__lock: 
                    self.__payload.clear()
            except Exception as e:
                print('failed to push metric',e)
        
            end_time = time.time()
                
    def __refreshDiskSpec(self):
        disk = NodeSpecification.diskList()
        self.__wsc.send(json.dumps({ 
            'path': 'post/spec/disk',
            'data':disk
            }))
        
            