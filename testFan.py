import os, json                                                                                                                             
import time                                                                                                                           
import requests                                                                                                                                                                                                                                             
import subprocess

def testFan(id_rig, step=5):   
    ## сначала стопарим майнер и удаляем старый файл рекалиброки
    subprocess.getstatusoutput("/hive/bin/miner stop") 
    try:
        subprocess.getstatusoutput("rm coolers.json")     
    except Exception:
        pass
                                                                                                                                                                                                                                                        
    effective_rpm = 0                                                                                                                                                                                                                                                         
    effective_handler = 0
    max_rpm = 0                                                                                                                                                                                                                                                               
    one_data_fan = 0                                                                                                                                                                                                                                                          
    print("НАЧИНАЮ РЕКОЛЕБРОВКУ КУЛЕРОВ")
    os.system("echo 1 >> /sys/class/hwmon/hwmon1/pwm2_enable")
    os.system("echo 0  >> /sys/class/hwmon/hwmon1/pwm2")
    time.sleep(30)        # убираем остаточное движение если до этого были раскручены                                                                                                                                                                                                                                                     
    old_rpm =  0   
    test = []

    for i in range(0, 75):
        give_rpm = i*int(step)                                                                                                                               
        print(give_rpm)                                                                                                                              
        os.system("echo " + str(give_rpm) +" >> /sys/class/hwmon/hwmon1/pwm2")
        time.sleep(5)                                                                                                                                
        (status,output)=subprocess.getstatusoutput("sensors | grep -i fan2")
        rpm1 = output.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        (status,output)=subprocess.getstatusoutput("sensors | grep -i fan2")
        rpm2 = output.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        time.sleep(2)
        (status,output)=subprocess.getstatusoutput("sensors | grep -i fan2")
        rpm3 = output.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        rpm = max(int(rpm1),int(rpm2),int(rpm3))
        
        if int(rpm) != 0:
            if one_data_fan == 0:
                if int(old_rpm) < int(rpm):
                    test.append({i:rpm})                                                                                                                                                                                                                                     
                else:
                    effective_rpm = int(rpm)
                    effective_handler = give_rpm
                    one_data_fan = 1

            old_rpm=rpm
        else:
            pass

        max_rpm = rpm

    if int(effective_handler) > 100:
        with open('coolers.json', "w+") as file:
            file.seek(0)
            file.write(json.dumps(test))
            file.truncate()
    else:
        send_mess(' RECALIBRATION is not accurate, try again.', id_rig)
        print("РЕКАЛИБРОВКА с шагом 5 пройти не удалось, пробую 10")
        testFan(id_rig, 10)

    print("РЕЗУЛЬТАТ РЕКАЛИБРОВКИ  >>  ", test)

    response = requests.post('http://ggc.center:8000/recalibrationOff/', data = {'id_rig': id_rig,
                                                                'effective_rpm':int(effective_rpm),
                                                                 'max_rpm':int(max_rpm),
                                                                 'effective_echo':effective_handler
                                                                 })


    try:
        os.system("/hive/bin/miner start")
    except Exception:
        pass
    return("Maximum speed of external coolers :"+str(max_rpm))

if __name__ == '__main__':
    testFan()
