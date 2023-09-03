

import subprocess

class NodeSpecification:
    def __init__(self) -> None:
        pass
    @staticmethod
    def diskList():
        diskNames = {}
        with open('/proc/partitions', 'r') as stat_file: 
            for line in stat_file: 
                part = line.split()
                if len(part) >=3: 
                    name = part[3] 
                    if name.startswith('sd') or name.startswith('vd'):#hdd,ssd or virtual disk
                        diskNames[name] = {'block':int(part[2]) } 
        command = ["lsblk","-l", "-o", "NAME,PHY-SEC"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            output_lines = result.stdout.strip().split('\n') 
            for line in output_lines:
                part = line.split()
                if part[0] in diskNames:
                    diskNames[part[0]]['sect'] = int(part[1])
        for key in diskNames:
            diskNames[key] = diskNames[key]['block'] * diskNames[key]['sect'] / 1024 #convert to kb
        return diskNames
     