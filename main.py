from CPUReading import CPUReading
from WsClient import WsClient
import time
import threading
import os
import requests  
import json
import re



# Clear console command based on the operating system
clear_console_command = "cls" if os.name == "nt" else "clear"

cpuReadings = []
fukuroIp = "http://192.168.30.1:5000/" 
global_pushInterval = 60
global_ExtractInterval = 10
pushThread = None
extractThread = None
doPush = True
doExtract = True


def main():
    clear_console()
    print("  ________  __    __  __   __  __    __  ______    _____\n"
          +" |   _____||  |  |  ||  | /  /|  |  |  ||   __  \\ /  _  \\\n" 
        + " |  |____  |  |  |  ||  |/  / |  |  |  ||  |__| ||  | |  |\n"
        + " |   ____| |  |__|  ||     /  |  |__|  ||      / |  | |  |\n"
        + " |  |       \\____   ||     \\   \\____   ||  |\\  \\ |  |_|  |\n"
        + " |__|            |__||__|\\__\\       |__||__| \\__\\ \\_____/\n"
        + "\n===========================================================\n")   
    input("Press Enter to continue...")
    username = "aa1122"
    password = "asd123"
    nodeId = "1"
    passKey = "asd123"
    while True:
        clear_console()
        print(f"FUKURO AGENT LOGIN\n\nUser Credentials\n\t1>username\t: {username}\n\t2>password\t: {password}"
              +f"\n\nNode Credentials\n\t3>nodeId\t: {nodeId}\n\t4>pass key\t: {passKey}\n5>LOGIN") 
        userInput = input("Select an option using number 1~5\n") 
        if userInput == "1":
            username = input("Insert username: ")
        elif userInput == "2":
            password = input("Insert user password: ")
        elif userInput == "3":
            nodeId = input("Insert node Id: ")
            try:
                nodeId = int(nodeId)
            except ValueError:
                print("Invalid id")
                
                nodeId = ""
                time.sleep(.5)
        elif userInput == "4":
            passKey = input("Inser node pass key: ")
        elif userInput == "5":
            if username == "" or password == "" or nodeId == "" or passKey == "":
                print("Incomplete credential")
                time.sleep(.5)
            else:
                print("Verifying user ...")
                response = requests.post(fukuroIp+"api/user/login",json= {
                    "username": username,
                    "password": password
                },headers={
                    "Content-Type": "application/json"
                })
                if response.status_code == 200:
                    print("User verified")
                    print("Verifying node ...") 
                    
                    getAccess = requests.get(fukuroIp+"api/node/access",json={
                            "nodeId": str(nodeId),
                            "passKey": passKey
                        },headers={
                        "Content-Type": "application/json",
                        "Authorization": response.json()["token"],
                        "uid": str(response.json()["uid"])
                    })
                    
                    if getAccess.status_code == 200:
                        print("Access Verified!! Starting monitoring")
                        time.sleep(.5)
                        monitoring(json.dumps( {"verify": {
                            "jwt": response.json()["token"],
                            "uid": str(response.json()["uid"]),
                            "nodeId": str(nodeId),
                            "passKey": passKey,
                            "client": "agent"
                        }}))
                        break
                    else:
                        print("Unable to access node pls recheck credential") 
                    time.sleep(1)
                    
                else:
                    print("Invalid user credentials")
            time.sleep(.5)
        else:
            print("invalid input")
            time.sleep(.5)
            
    
 

def monitoring(jsonVerifyWS): 
    #ws er
    print(jsonVerifyWS) 
    wsc = WsClient("ws://192.168.30.1:5000",jsonVerifyWS,restartPushThread,setInterval)
    wsc.run() 
    print("after")
    global pushThread, extractThread
    extractThread = threading.Thread(target=extractMetric)
    pushThread = threading.Thread(target=pushMetrics, args=(wsc,))
    pushThread.start()  
    extractThread.start()

def extractMetric():
    print("extract")
    global doExtract, global_ExtractInterval
    while doExtract: 
        
        #get first reading ignore time
        reading1,_ = CPUReading.getCurrent() 

        with lock:
            extInterval = global_ExtractInterval
        while doExtract and extInterval > 0:
            time.sleep(1)
            extInterval -= 1
        
        #get second reading and timestamp
        reading2,readTime = CPUReading.getCurrent() 
        
        global cpuReadings
        #parse reading into each cpu
        for i in range(len(reading1)): 
            tmpRead = CPUReading(reading1[i],reading2[i],readTime) 
            with lock:
                cpuReadings.append(tmpRead.getJSON()) 
            
def pushMetrics(wsc):
    print("push metric") 
    global global_pushInterval, doPush
    while doPush: 
        with lock:
            pushInterval = global_pushInterval
        print(f"pushInterval{pushInterval}") 
        while doPush and pushInterval > 0:
            time.sleep(1) 
            pushInterval -= 1
        global cpuReadings 
        
        payload = { 
            "readings":{
                "cpu":[]
                        
            } 
        }
        #access global var of readings
        with lock:
            payload["readings"]["cpu"] = cpuReadings.copy()
            cpuReadings.clear()
        
        #minify payload
        payload = re.sub(r"\s+|\n","",json.dumps(payload))
        payload = payload.replace('_',' ')
                
        #send payload 
        wsc.send(payload)
        print("submited")
            
        

def restartPushThread(wsc): 
    global pushThread, doPush , doExtract, extractThread
    doPush = False
    doExtract = False
    pushThread.join()
    extractThread.join()
    pushThread = threading.Thread(target=pushMetrics, args=(wsc,))
    extractThread = threading.Thread(target=extractMetric)
    doPush = True
    doExtract = True
    pushThread.start() 
    extractThread.start()
    
def setInterval(iv,iv2):
    global global_pushInterval, global_ExtractInterval
    with lock:
        global_pushInterval = iv
        global_ExtractInterval = iv2
    

def clear_console():
    os.system(clear_console_command)
    
lock = threading.Lock()
main()