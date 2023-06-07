import websocket
import threading
 
class WsClient:
    def __init__(self,url,verifyJSON,restartThread,setInterval):
        self.ws = websocket.WebSocketApp(url,
                                         on_open=self._onOpen,
                                      on_message=self._onMessage,
                                      on_error=self._onError,
                                      on_close=self._onClose)
        self.verifyJSON = verifyJSON  
        self.restartThread = restartThread
        self.setInterval = setInterval
    
    def _onOpen(self,ws):
        print("open") 
        self.ws.send(self.verifyJSON) 
    
    def _onMessage(self,ws,message):
        print(message) 
        if message == "live interval": 
                self.setInterval(3,3)
                self.restartThread(self)
        elif message == "norm interval": 
                self.setInterval(60,10)
                self.restartThread(self)
                
    
    def _onError(self,ws,error):
        print(error)
        
    def _onClose(self,ws,closeStatus,closeMsg):
        print("closed")
        
    def run(self):
        threading.Thread(target=self.ws.run_forever).start()
    
    def send(self, payload): 
        self.ws.send(payload)
    
    