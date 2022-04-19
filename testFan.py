import os                                                                                                                             
import time                                                                                                                           
import requests                                                                                                                                                                                                                                             
import subprocess

def testFan(id_rig):   
    subprocess.run(['miner', 'stop'], stdout=subprocess.PIPE)                                                                                                                                                                                                                                                       
    effective_rpm = 0                                                                                                                                                                                                                                                         
    effective_handler = 0
    max_rpm = 0                                                                                                                                                                                                                                                               
    one_data_fan = 0                                                                                                                                                                                                                                                          
    print("НАЧИНАЮ РЕКОЛЕБРОВКУ КУЛЕРОВ")
    os.system("echo 1 >> /sys/class/hwmon/hwmon1/pwm2_enable")
    os.system("echo 0  >> /sys/class/hwmon/hwmon1/pwm2")
    time.sleep(30)        # убираем остаточное движение если до этого были раскручены                                                                                                                                                                                                                                                     
    old_rpm =  0   

    for i in range(1, 55):
        give_rpm = i*5                                                                                                                               
        print(give_rpm)                                                                                                                              
        os.system("echo " + str(give_rpm) +" >> /sys/class/hwmon/hwmon1/pwm2")
        time.sleep(5)                                                                                                                                
        (status,output)=subprocess.getstatusoutput("sensors | grep -i fan2")
        rpm1 = output.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        time.sleep(3)   
        (status,output)=subprocess.getstatusoutput("sensors | grep -i fan2")
        rpm2 = output.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        time.sleep(3)
        (status,output)=subprocess.getstatusoutput("sensors | grep -i fan2")
        rpm3 = output.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        rpm = max(int(rpm1),int(rpm2),int(rpm3))
        
        if one_data_fan == 0:
            if int(old_rpm) < int(rpm):
                pass                                                                                                                                                                                                                                     
            else:
                effective_rpm = int(rpm)
                effective_handler = give_rpm
                one_data_fan = 1
                break

        old_rpm=rpm


        max_rpm = rpm
    response = requests.post('http://ggc.center:8000/recalibrationOff/', data = {'id_rig': id_rig,
                                                                'effective_rpm':int(effective_rpm),
                                                                 'max_rpm':int(max_rpm),
                                                                 'effective_echo':effective_handler
                                                                 })
    
    subprocess.run(['miner', 'start'], stdout=subprocess.PIPE)
    return("Maximum speed of external coolers :"+str(max_rpm))

if __name__ == '__main__':
    testFan()
