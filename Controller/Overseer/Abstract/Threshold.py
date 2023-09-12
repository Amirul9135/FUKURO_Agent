
import threading
import time 
import re
import json

class Threshold:
    def __init__(self,sender,cooldown,tick):
        self.__all = []
        self.__cooldown = cooldown
        self.__tick = tick
        self.__lock :threading.Lock = threading.Lock() 
        self.__send = sender
    
   
    
    def evaluate(self,value,payload): 
        reached = self.__check(value)  
        tmpReached = []
        for threshold in reached: 
            if self.__checkTick(threshold):
                tmpReached.append(threshold) 
        if len(tmpReached)> 0 :
            print("alert",value,threshold,payload)       
            payload = re.sub(r"\s+|\n","",json.dumps(payload)) 
            try:
                self.__send(payload) 
                for th in tmpReached:
                    self.__startCooldown(th)
            except Exception as e:
                print('threshold fail',e)
                
    def updateCooldown(self,value):
        with self.__lock:
            self.__cooldown = value
        for th in self.__all:
            self.__refresh(th)
         
        
    #vlaues should be array of float representing the threshold
    def updateThresholds(self,values): 
        idx = 0
        while idx < len(self.__all):
            found = False
            for newval in values:
                if newval == self.__all[idx]["val"]:
                    found = True
            if not found: #if existing value is no longer in new val remove
                self.__refresh(self.__all[idx]) #refresh the threshold to clear the thread
                self.__all = self.__all[:idx] + self.__all[idx+1:]
            else: 
                values.remove(self.__all[idx]["val"])
                #if existing value does exist in new value also just proceed 
                idx += 1  
        for val in values:
            self.__add(val)
                  
        
    def updateTick(self,val):
        self.__tick = val
    
    def stopAll(self):
        for cd in self.__all:
            self.__refresh(cd)
        
    def __add(self,value):
        index = 0
        while index < len(self.__all) and self.__all[index]["val"] <= value:
            if self.__all[index]["val"] == value: 
                return #same val no need usik
            index += 1  
        self.__all.insert(index,{
            "val":value,
            "tick":0,
            "cooldown": False,
            "thread": None
        })
    def __checkTick(self,cd): 
        cd["tick"] = cd["tick"] + 1
        if cd["tick"] >= self.__tick:
            return True
        else:
            return False
        
    def __check(self,value):
        reach = []
        for threshold in self.__all:
            if  not threshold["cooldown"] and value >= threshold["val"]:
                reach.append(threshold) 
            else:
                threshold["tick"] = 0 #if not reach reset tick
        return reach
    
    def __startCooldown(self,cd):
        cd["cooldown"] = True
        cd["thread"] = threading.Thread(target=self.__cooldownProcess, args=(cd,))
        cd["thread"].start()
    
    def __cooldownProcess(self,cd):
        cooldown = 0
        #load cooldown duration'
        with self.__lock:
            cooldown = self.__cooldown
            
        #loop as long as is cooling down checking both flag and count'
        while cd["cooldown"] and cooldown > 0:
            cooldown -= 1
            time.sleep(1)
        
        #update cooldown status'
        with self.__lock: 
            cd["cooldown"] = False
            cd["tick"] = 0
        return 
     
    
    def __refresh(self,cd):
        with self.__lock:
            cd["cooldown"] = False
        cd["tick"] = 0
        if cd["thread"] != None and cd["thread"].is_alive():
            cd["thread"].join()
    
         