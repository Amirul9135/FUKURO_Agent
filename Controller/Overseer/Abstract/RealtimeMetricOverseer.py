from Controller.WsClient import WsClient
from Controller.Overseer.Abstract.MetricOverseer import MetricOverseer 
import time
import threading
import json



class RealtimeMetricOverseer(MetricOverseer):
    
    def __init__(self, wsc: WsClient, payload:dict,interval = None, threshold = None, thresholdTick = None, alertCooldown = None):
        
        #realtime default interval would be 1 second'
        interval = interval if interval is not None else 1
        
        super().__init__(wsc,interval)
        
    def _transmitReading(self,label:str,reading:dict):
        
        payload = {
            "path":"realtime/" + label,
            "data": reading
        }
        try:
            self._sendMessage(json.dumps(payload).replace('_',' '))
        except Exception as e:
            print('realtime failed',e)