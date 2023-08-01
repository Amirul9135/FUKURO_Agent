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

#intervals
global_pushInterval = 60 
global_ExtractInterval = 15 #configurable

#Threads
pushThread = None
extractCPUThread = None

#Push and Extract Flag
doPush = True
doExtract = True

##### Realtime settings

#Realtime threads
RTCpuThread = None

#Realtime intervals
RTCpuInterval = 1

#Realtime flags
RTCpu = False

# signals
CPUAlertCooldown = 60 #second #configurable
isCPUAlertCooldown = False
CPUAlertThreshold = 80 #configurable



def main():
    #skip()
    #return
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
    wsc = WsClient("ws://192.168.30.1:5000",jsonVerifyWS,restartPushThread,intervalController,realTimeController)
    wsc.run() 
    print("after")
    global pushThread, extractCPUThread
    extractCPUThread = threading.Thread(target=extractCPU, args=(wsc,))
    pushThread = threading.Thread(target=pushMetrics, args=(wsc,))
    pushThread.start()  
    extractCPUThread.start()

def extractCPU(wsc):
    
    print("extract cpu")
    global doExtract, global_ExtractInterval,cpuReadings, isCPUAlertCooldown
    while doExtract: 
        
        # get first reading ignore time
        reading1,_ = CPUReading.getCurrent() 

        time.sleep(1)
        
        # get second reading and timestamp
        reading2,readTime = CPUReading.getCurrent() 
        
        # append cpu reading into the cache 
        cpuMetric = CPUReading(reading1,reading2,readTime)
        with lock:
            cpuReadings.append(cpuMetric.getJSON())  
            extInterval = global_ExtractInterval
        print(f"reading {cpuMetric.getTotal()}")
        if cpuMetric.getTotal() >= CPUAlertThreshold:
            print('th')
            if not isCPUAlertCooldown:
                payload = {
                    "alert":{
                        "type":"cpu",
                        "reading": cpuMetric.getJSON()
                    }
                }
                payload = json.dumps(payload)
                payload = payload.replace('_',' ')
                wsc.send(payload)
                print("alerts")
                isCPUAlertCooldown = True
                threading.Thread(target=cooldownCPU).start()
        
            
        # cooldown according to extract interval
        # wait by 1 second to allow instant reset when necessary
        while doExtract and extInterval - 1 > 0:
            time.sleep(1)
            extInterval -= 1

def extractCPURealtime(wsc): 
    global RTCpu,RTCpuInterval
    while RTCpu: 
        # get first reading ignore time
        reading1,_ = CPUReading.getCurrent() 

        time.sleep(1)
        
        # get second reading and timestamp
        reading2,readTime = CPUReading.getCurrent() 
        payload = {
            "realtime":{
                "cpu": CPUReading(reading1,reading2,readTime).getJSON()
            }
        } 
        payload = json.dumps(payload)
        payload = payload.replace('_',' ')
        wsc.send(payload)
        print("send cpu realtime")
        with lock:
            tmpInterval = RTCpuInterval
        while RTCpu and tmpInterval - 1 > 0:
            time.sleep(1)
            tmpInterval -= 1
        
            
def pushMetrics(wsc):
    print("saving metric") 
    global global_pushInterval, doPush
    while doPush: 
        with lock:
            pushInterval = global_pushInterval
        
        # cooldown push metrics,
        # wait by 1 second to allow instant shift in interval
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
    global pushThread, doPush , doExtract, extractCPUThread
    doPush = False
    doExtract = False
    pushThread.join()
    extractCPUThread.join()
    pushThread = threading.Thread(target=pushMetrics, args=(wsc,))
    extractCPUThread = threading.Thread(target=extractCPU, args=(wsc,))
    doPush = True
    doExtract = True
    pushThread.start() 
    extractCPUThread.start()
    
# function to modify intervals for historical reaing
def intervalController(config):
    if "push" in config:
        global global_pushInterval
        with lock:
            global_pushInterval = config["push"]
    elif "extract" in config:
        global global_ExtractInterval
        with lock:
            global_ExtractInterval = config["extract"] 

 
def cooldownCPU():
    cooldown = 0
    global isCPUAlertCooldown,CPUAlertCooldown
    while isCPUAlertCooldown and cooldown < CPUAlertCooldown:
        cooldown = cooldown + 1
        time.sleep(1)
    with lock:
        isCPUAlertCooldown = False
        
        


# controller function for realtime metrics extraction
# param config as hash
# {
#  "cpu":  
# }
def realTimeController(wsc,config):
    if "cpu" in config:
        # cpu configuration
        global RTCpuThread, RTCpu
        if config["cpu"] == "start":
            print("Starting realtime cpu extraction")
            RTCpuThread = threading.Thread(target=extractCPURealtime, args=(wsc,))
            RTCpu = True
            RTCpuThread.start()  
        elif config["cpu"] == "stop":
            print("Stopping realtime cpu extraction")
            RTCpu = False
            RTCpuThread.join()
            

def clear_console():
    os.system(clear_console_command)
    
lock = threading.Lock()
main()