from Controller.WsClient import WsClient
import subprocess
import json
import os 
from multiprocessing import Process
import pexpect

class CommandExecutor:
    def __init__(self,wsc:WsClient) :
        self.__wsc:WsClient = wsc
        self.__wsc.addListener("command", self.__execute)  
        
    
    def __execute(self,data):  
        try:
            if 'isTool' in data:
                Process(target=self.__executeTool, args=(data,)).start() 
            else:
                Process(target=self.__executeCommand, args=(data,)).start() 
        except Exception as e:
            print(e)
        
    def __executeCommand(self,data):  
        print('command')
        try:
            os.chdir(data['dir']) #change to user current working directory  
        except Exception as e:
            response_data = {
            'path': 'command/' + data['id'],
            'data': f"Invalid Directory: {str(e)}"
            }
            self.__send_response(response_data)
            return
        
        parts = data['cmd'].split()
        response_data= {}
        if parts[0] == 'cd':
            if len(parts) == 2:
                try:
                    os.chdir(data['dir'])
                    os.chdir(parts[1])  # Change the current directory
                    current_directory = os.getcwd()
                    response_data = {
                        'path': 'command/cd/' + data['id'],
                        'data': f"Changed directory to: {current_directory}"
                    }
                except Exception as e:
                    response_data = {
                        'path': 'command/' + data['id'],
                        'data': f"Failed to change directory: {str(e)}"
                    }
            else:
                response_data = {
                    'path': 'command/' + data['id'],
                    'data': "Invalid 'cd' command format"
                } 
        else:
            try:
                process = subprocess.Popen(
                    data['cmd'],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                output, errors = process.communicate(timeout=30)  # Adjust the timeout as needed

                if process.returncode == 0:
                    response_data = {'path': 'command/' + data['id'], 'data': output}
                else:
                    response_data = {'path': 'command/' + data['id'], 'data': errors}

            except subprocess.TimeoutExpired:
                response_data = {'path': 'command/' + data['id'], 'data': 'Command timed out'} 

            except Exception as e:
                response_data = {'path': 'command/' + data['id'], 'data': str(e)} 
        

        self.__send_response(response_data)
    
    def __executeTool(self,data):
        
        try:
            os.chdir(data['dir']) #change to user current working directory  
        except Exception as e:
            response_data = {
            'path': 'command/' + data['id'],
            'data': f"Invalid Directory: {str(e)}"
            }
            self.__send_response(response_data)
            return
         
        try: 
            child = pexpect.spawn(data['cmd'])   
 
            child.expect(pexpect.TIMEOUT, timeout=1)

            # Capture the output
            output = child.before.decode('utf-8')

            # Close the child process
            child.close()

            response_data = {'path': 'command/' + data['id'], 'data': output} 

        except Exception as e:
            response_data = {'path': 'command/' + data['id'], 'data': str(e)} 
        
        self.__send_response(response_data)
    
    def __send_response(self, response_data): 
        self.__wsc.send(json.dumps(response_data).replace('_', ' '))