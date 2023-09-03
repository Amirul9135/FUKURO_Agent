from Controller.Overseer.Abstract.IntervalMetricOverseer import IntervalMetricOverseer 
from Controller.WsClient import WsClient 
from Model.DiskReading import DiskReading 
import time
import copy

class DiskOverseer(IntervalMetricOverseer):
    
    def __init__(self, wsc: WsClient, payload: dict,diskList:dict,interval = None, threshold = None, thresholdTick = None, alertCooldown = None):
        super().__init__(wsc, payload,interval,threshold,thresholdTick,alertCooldown) 
        wsc.addListener("interval/dsk", self.updateInterval)
        wsc.addListener("alert/cooldown/dsk", self.updateAlertCooldown)
        wsc.addListener("alert/threshold/dsk",self.updateThreshold)
        wsc.addListener("alert/threshold/tick/dsk", self.updateThresholdDuration) 
        wsc.addListener("toggle/dsk", lambda val: self.start() if val else self.stop())
        wsc.addListener("spec/disk", self.__updateDisklist) 
        self.__disk = diskList
        DiskReading.getSectorSize(self.__disk)
 
    def _metricExtraction(self): 
        #Extract 2 reading at 1 sec interval timepoint' 
        reading1 = copy.deepcopy(self.__disk )
        reading2 = copy.deepcopy(self.__disk ) 
        start_time,_ = DiskReading.readCurrentProc(reading1) 
        time.sleep(1) 
        end_time,t2 = DiskReading.readCurrentProc(reading2)  
        elapsed = (end_time - start_time) * 1000  

        for key in reading2:
            metric = DiskReading(reading1[key]['reading'],reading2[key]['reading'],reading2[key]['sect'],elapsed,t2)
            self._addReading(DiskReading.metricLabel(),metric.toJSON(key))  
        
         
    def __updateDisklist(self,val):
        ''
        self.__disk = {}
        for name in val:
            self.__disk[name] = DiskReading.diskStruct()
        DiskReading.getSectorSize(self.__disk)