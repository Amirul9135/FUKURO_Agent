import websocket
import threading
import json
 
class WsClient:
    
    'initialize the web socket and connect'
    def __init__(self,url,verification):
        self.__verification:str = verification   
        self.__listeners:dict = {}
    
    'send the verification string to allow server identify the agent'
    def __onOpen(self):
        print("open") 
        self.__ws.send(self.__verification) 
    
    
    def __onMessage(self,ws,message):
        'parse the message to identify task or multiple task'
        try:
            parsed = json.loads(message)
            if isinstance(parsed,dict):
                self.__executeTask(message)
            elif isinstance(parsed,list):
                for task in parsed:
                    self.__executeTask(task)
        except json.JSONDecodeError:
            print("message in unsupported format received")
        
    def __executeTask(self,task):
        'task should be a dict with 2 key path and data(optional)'
        
        if task['path'] in self.__listeners:
            'execute the task using listener in the map'
            if 'data' in task:
                self.__listeners[task['path']](task['data'])
            else:
                self.__listeners[task['path']]()
    
    def __onClose(self):
        print("closed")
        
    def __onError(self):
        print('web socket error')
        
    'send message in string to the server'
    def send(self, message): 
        print('send' + message)
        'self.__ws.send(message)'
        
    'add a function to the function mapping using the key in first parameter'
    def addListener(self,key:str, action):
        self.__listeners[key] = action
    
    'remove the function mapped to the key in parameter from the mapping'
    def clearListener(self,key):
        self.__listeners.pop(key)
    
    def run(self):
        'threading.Thread(target=self.__ws.run_forever).start()'
    
    