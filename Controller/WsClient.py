import websocket
import threading 
import json
 
class WsClient:
    
    #initialize the web socket and connect'
    def __init__(self,url,verification):
        self.__verification:str = verification   
        self.__listeners:dict = {} 
        self.__ws:websocket.WebSocketApp = websocket.WebSocketApp(url,
                                         on_open=self.__onOpen,
                                      on_message=self.__onMessage,
                                      on_error=self.__onError,
                                      on_close=self.__onClose)
        self.__isReady:bool = False
        self.__connected:bool = False
    
    #send the verification string to allow server identify the agent'
    def __onOpen(self,ws):
        print("open") 
        self.__ws.send(json.dumps({"path":"verify/agent",
                        "data":self.__verification
            })) 
    
    

    
    def __onMessage(self,ws,message):
        print("received ",message) 
        #parse the message to identify task or multiple task
        try:
            parsed = json.loads(message)
            if(type(parsed) == str):
                parsed = json.loads(parsed) 
            if isinstance(parsed,dict):
                self.__executeTask(parsed)
            elif isinstance(parsed,list):
                print('listo')
                for task in parsed: 
                    self.__executeTask(task)
        except json.JSONDecodeError:
            print("message in unsupported format received")
        
    def __executeTask(self,task):
        #task should be a dict with 2 key path and data(optional) 
        if task['path'] == "connected":
            
            self.__isReady = True 
            self.__connected = True
        if task['path'] in self.__listeners:
            #execute the task using listener in the map
            if 'data' in task:
                self.__listeners[task['path']](task['data'])
                print('executed ' , task['path'] , ' value ' , task['data'])
            else:
                self.__listeners[task['path']]() 
                print('executed ' , task['path'])
    
    def __onClose(self,ws,close_status_code,close_msg):
        print("closed")
        self.run()
        
    def __onError(self,ws,error):
        print('web socket error',error)
        if(isinstance(error,AttributeError) and 'errno' in error and error.errno == 111):
            print(error.errno)   
            self.__isReady = True
            self.__connected - False
        
    #send message in string to the server'
    def send(self, message): 
        print('send' + message)
        self.__ws.send(message)
        
    #add a function to the function mapping using the key in first parameter
    def addListener(self,key:str, action):
        self.__listeners[key] = action
    
    #remove the function mapped to the key in parameter from the mapping
    def clearListener(self,key):
        self.__listeners.pop(key)
    
    def run(self):
        threading.Thread(target=self.__ws.run_forever).start()
        
    def isReady(self):
        return self.__isReady
    
    def isConnected(self):
        return self.__connected
    
    