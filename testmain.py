from Controller.MonitoringController import MonitoringController
from Controller.CommandExecutor import CommandExecutor
from Controller.WsClient import WsClient  
import time 

##
from Model.MEMReading import MEMReading


def main():
    print("start")
    localIp = "ws://192.168.8.102:5000"
    liveIp = "ws://139.59.233.99:5001"

    ws = WsClient(liveIp,{
        "nodeId":1,
        "passKey":"asd123",
        "jwt":"eyJ1c2VyIjp7ImlkIjoxLCJuYW1lIjoiYW1pcnVsIGFzcmFmIiwidXNlcm5hbWUiOiJhYTExMjMifSwiaWF0IjoxNjk0MzQ0NDY0fQ.y71ZljP0WApsYjo-7tZSPtUZcYPs6pOB2vVyI2pZ_hI",
        "uid":1
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

#main()
test =  MEMReading()
print(test.toJSON())

main()

