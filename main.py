from CPUReading import CPUReading
import time

cpuReadings = []

def main():
    print("dalam main")  
    monitoring()


def monitoring():
    while(1):
        print("monitor")
        reading1,_ = CPUReading.getCurrent() 
        
        time.sleep(5)
        reading2,readTime = CPUReading.getCurrent() 
        for i in range(len(reading1)):
            tmpRead = CPUReading(reading1[i],reading2[i],readTime)
            print(tmpRead.getJSON())
            cpuReadings.append(tmpRead)
            
            
        
    
main()