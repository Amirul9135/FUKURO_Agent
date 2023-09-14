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

    ws = WsClient(localIp,{
        "nodeId":2,
        "passKey":"qwe123",
        "jwt":"eyJ1c2VyIjp7ImlkIjoyLCJuYW1lIjoiYW1pcnVsIiwidXNlcm5hbWUiOiJhbWlydWw5OSJ9LCJpYXQiOjE2OTQ2NzQ1MjV9.qlOLUIQcdgvlGrii2dZMxx67rFvcYVqPjeiPTrctEfA",
        "uid":2
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
   
main()