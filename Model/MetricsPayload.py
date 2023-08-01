class MetricsPayload:
    def __init__(self):
        self._cpu = []
        self._mem = []
        
    def addCPU(self,val):
        self._cpu.append(val)
    
    def addMem(self,val):
        self._mem.append(val)
    
    def clear(self):
        self._cpu.clear()
        self._mem.clear()