from Controller.MonitoringController import MonitoringController
from Controller.CommandExecutor import CommandExecutor
from Controller.WsClient import WsClient  
import time

##
from Model.MEMReading import MEMReading


def main():
    print("start")

    ws = WsClient("ws://192.168.8.102:5000",{
        "nodeId":1,
        "passKey":"asd123",
        "jwt":"eyJ1c2VyIjp7ImlkIjoxLCJuYW1lIjoiYW1pcnVsIGFzcmFmIiwidXNlcm5hbWUiOiJhYTExMjMifSwiaWF0IjoxNjkzMjczNTk0fQ.HG2SJXWqhh6JIwIhSGMnDsNWilfKfCFzO6iNdXjUx1M",
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

