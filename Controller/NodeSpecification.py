

import subprocess
import os

class NodeSpecification:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def cpu_spec():
        spec = {}
        cpu = open('/proc/cpuinfo', 'r').read() 
        lines = cpu.split('\n')
        for line in lines:
            part = line.split(':')    
            if len(part) > 0 and "model name" in part[0].lower(): 
                spec['name'] = part[1].strip()
            if len(part) > 0 and "cpu cores" in part[0].lower(): 
                spec['cores'] = part[1].strip()
            if len(part) > 0 and "cache size" in part[0].lower(): 
                spec['cache'] = part[1].strip()
            if len(part) > 0 and "cpu mhz" in part[0].lower(): 
                spec['freq'] = part[1].strip()
        return spec
        
    @staticmethod
    def memTotal():
         with open('/proc/meminfo', 'r') as meminfo_file:
            for line in meminfo_file:
                parts = line.split(':')
                if len(parts) == 2:
                    key = parts[0].strip()
                    if(key == "MemTotal"):
                        return parts[1].strip()
    
    @staticmethod
    def ip_address():
        ip = os.popen("hostname -I").read()
        return ip.strip()
    
    @staticmethod
    def diskList():
        diskNames = {} 
        command = ["lsblk","-b","-l", "-o", "NAME,PHY-SEC,SIZE,FSUSED"] #-b fix all to bytes
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) 
        if result.returncode == 0: 
            output_lines = result.stdout.strip().split('\n') 
            for line in output_lines:
                part = line.split()
                if part[0].startswith('sd') or part[0].startswith('vd'):#hdd,ssd or virtual disk
                    diskNames[part[0]] = {}  
                    diskNames[part[0]]['size'] = round( (int(part[2]) / 1024),2) #bytes to kb
                    if len(part) > 3: 
                        diskNames[part[0]]['used'] = round((int(part[3]) / 1024),2) #bytes to kb
                    else:
                        diskNames[part[0]]['used'] = 0 
        for key in diskNames:
            if diskNames[key]['used'] == 0:
                for key2 in diskNames:
                    if key2.startswith(key) and key2 != key:
                        diskNames[key]['used'] += diskNames[key2]['used']
        return diskNames

 