import argparse
import daemonize 
import signal
import os
import sys
import time
from Controller.WsClient import WsClient
from Controller.MonitoringController import MonitoringController
from Controller.CommandExecutor import CommandExecutor

import requests

# Daemonized application logic
class FUKURO:
    
    @staticmethod
    def IP():
        return '192.168.8.102:5000'
    
    def __init__(self, username, password, passkey, nodeId):
        self.ws = None
        self.username = username
        self.password = password
        self.passkey = passkey
        self.nodeId = nodeId
        self.__monitor = None
        self.__cmd = None
        self.__jwt = None
        self.__uid = None

    def start(self):
        # attempt to start, perform login and verification
        ''
        
        response = requests.post('http://'+FUKURO.IP()+"/api/user/login",json= {
                    "username": self.username,
                    "password": self.password
                },headers={
                    "Content-Type": "application/json"
                })
        if response.status_code == 200:
            self.__jwt = response.json()["token"],
            self.__uid = str(response.json()["uid"]),
            getAccess = requests.post('http://'+FUKURO.IP()+"/api/node/access",json={
                            "nodeId": str(self.nodeId),
                            "passKey": self.passkey
                        },headers={
                        "Content-Type": "application/json",
                        "Authorization": response.json()["token"],
                        "uid": str(response.json()["uid"])
                    })
            if getAccess.status_code == 200:
                print('starting') 
                daemon = daemonize.Daemonize(
                    app="FUKURO_Agent",
                    pid=os.path.join("/var/run", "FUKURO_Agent.pid"),
                    action=self.__run,
                    foreground=False
                ) 
                try:
                    daemon.start()
                except Exception as e:
                    print(f"Error: {str(e)}")
                
            else:
                print('failed to start, user does not have access')
                
        else:
            print('failed to start, invalid user credential')
        
    def stop(self,passKey):
        # Stop and clean up your background process here
        if passKey != self.passkey:
            print("pass key doesn't match")
            return
        if self.__monitor:
            self.__monitor.stopAll() 
        if self.ws:
            self.ws.close()  # Implement a method to gracefully close your WebSocket connection
            self.ws = None
        print("Daemon stopped.")
    
    def __run(self):  
        signal.signal(signal.SIGTERM, self.stop)
        self.ws = WsClient("ws://"+FUKURO.IP(), {
            "nodeId": self.nodeId,
            "passKey": self.passkey,
            "jwt": self.__jwt,  # You may set this here or load it from a file/config
            "uid": self.__uid
        })
        while not self.ws.isConnected():
            while(not self.ws.isReady()):
                print('Testing connection to FUKURO server..',flush=True)
                self.ws.run()
                time.sleep(1) 
            if (not self.ws.isConnected()):
                print("Unnable to connect to server")
        print("Connected, starting monitoring in background")
        self.__monitor = MonitoringController(self.ws)
        self.__cmd = CommandExecutor(self.ws)

# CLI for configuration and control
def cli():
    parser = argparse.ArgumentParser(description="FUKURO")
    # Define positional arguments
    parser.add_argument("action", choices=["start", "stat","stop"], help="Action to perform (start, stop)")
    parser.add_argument("passkey",nargs="?",  help="Passkey")
    parser.add_argument("nodeId",nargs="?",  type=int, help="Node ID")
    parser.add_argument("username",nargs="?",  help="Username")
    parser.add_argument("password",nargs="?",  help="Password") 

    args = parser.parse_args()

    # Access the values of the positional arguments
    action = args.action
    
    # Perform actions based on the values
    if action == "start":
        # Start the daemon with the provided credentials
        if not all([args.username, args.password, args.passkey, args.nodeId]):
            parser.error("When starting, all of --username, --password, --passkey, and --nodeId are required.")
        username = args.username
        password = args.password
        passkey = args.passkey
        nodeId = args.nodeId
        print(f"Starting FUKURO Monitoring ")
        app = FUKURO(username,password,passkey,nodeId)
        app.start()
    elif action == "stop":
        if not all([args.passkey]):
            parser.error("When stopping, passkey are required")
        # Stop the daemon
        print("Stopping FUKURO Monitoring")  
        try:
            ''
            with open("/var/run/FUKURO_Agent.pid", "r") as pid_file:
                pid = int(pid_file.read())
                os.kill(pid, signal.SIGTERM)
                print("FUKURO Monitoring stopped")  
        except Exception as e:
            print(e)
    elif action == "stat":
        print('status')
        pid_file = "/var/run/FUKURO_Agent.pid" 
        if os.path.exists(pid_file):
            with open(pid_file, "r") as pidfile:
                pid = int(pidfile.read().strip())
                if os.path.exists(f"/proc/{pid}"):
                    print('running')
                    return
        print('stopped')
                

if __name__ == "__main__":
    # Check if the user provided command-line arguments
    if len(sys.argv) > 1:
        cli()
    else:
        print('no argument')
        print('please provide \naction passKey nodeId username password '
              '\nin correct order.\naction: start or stop\nusername and password is your personal credential'
              '\nnodeId and passKey can be obtained after registering new node via the mobile app'
              )
        # If no arguments are provided, run the daemonized application
        #MyDaemonizedApp(None, None, None, None).start()
