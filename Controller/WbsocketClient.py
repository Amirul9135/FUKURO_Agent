import websocket
import threading
 
class WsClient:
    
    def __init__(self,url,verifyJSON,restartThread,intervalController,rtController):
        self.ws = websocket.WebSocketApp(url,
                                         on_open=self._onOpen,
                                      on_message=self._onMessage,
                                      on_error=self._onError,
                                      on_close=self._onClose)
        self.verifyJSON = verifyJSON  
        self.restartThread = restartThread
        self.intervalController = intervalController
        self.realtimeController = rtController
    
    def _onOpen(self,ws):
        print("open") 
        self.ws.send(self.verifyJSON) 
    
    def _onMessage(self,ws,message):
        print(f"recieved{message}")  
        if message == "RT_CPU":
            self.realtimeController(self,{
                "cpu":"start"
            })
        elif message == "NOCLIENT":
            self.realtimeController(self,{
                "cpu":"stop"
            })
            
                
    
    def _onError(self,ws,error):
        print(error)
        
    def _onClose(self,ws,closeStatus,closeMsg):
        print("closed")
        
    def run(self):
        threading.Thread(target=self.ws.run_forever).start()
    
    def send(self, payload): 
        self.ws.send(payload)
    
    