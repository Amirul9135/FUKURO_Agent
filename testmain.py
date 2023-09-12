from datetime import datetime
import json
import re
import requests
from Controller.MonitoringController import MonitoringController
from Controller.CommandExecutor import CommandExecutor
from Controller.WsClient import WsClient  
import time 
import pytz

##
from Model.MEMReading import MEMReading


def main():
    print("start")
    localIp = "ws://192.168.8.102:5000"
    liveIp = "ws://139.59.233.99:5001"

    ws = WsClient(liveIp,{
        "nodeId":1,
        "passKey":"asd123",
        "jwt":"eyJ1c2VyIjp7ImlkIjoyMCwibmFtZSI6Ik11aGFtbWFkIEFtaXJ1bCBBc3JhZiBiaW4gTXVzdGFmYSAiLCJ1c2VybmFtZSI6ImFtaXJ1bDk5In0sImlhdCI6MTY5NDQ5MDA5M30.pnQFfAAdVKm4AOVWkXYtn7n2Pr-IqjxRlUvEyU44gSA",
        "uid":20
    })
    ws.run()
    print("connecting")
    while(not ws.isReady()):
        print('Connecting..',flush=True)
        time.sleep(0.5) 
    if (not ws.isConnected()):
        print("unnable to connect to server")
    else:
        print("connected")
        cont = MonitoringController(ws)
        ext = CommandExecutor(ws)

def dateTest():
    requests.get('http://192.168.8.102:5000/',json= {
                    "string" : datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                    "dt" : datetime.isoformat(datetime.now(pytz.utc))
                },headers={
                    "Content-Type": "application/json"
                })
  
print(datetime.isoformat(datetime.now(pytz.utc))) 

payload = {"string":"strsomething asd dsequdsa","dt":datetime.isoformat(datetime.now(pytz.utc)),"num":12030.2}
print(payload)
payload = re.sub(r"\s+|\n","",json.dumps(payload)) 
print(payload)
main()