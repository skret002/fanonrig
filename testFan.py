import os, json                                                                                                                             
import time                                                                                                                           
import requests                                                                                                                                                                                                                                             
import subprocess
from handler_messeges import transmit_mess as send_mess

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
    time.sleep(40)        # убираем остаточное движение если до этого были раскручены                                                                                                                                                                                                                                                     
    old_rpm =  0   
    old_average_rpm = 0
    test = []

    for i in range(0, 75):
        give_rpm = i*int(step)                                                                                                                                                                                                                                                           
        os.system("echo " + str(give_rpm) +" >> /sys/class/hwmon/hwmon1/pwm2")
        time.sleep(5)                                                                                                                                
        (status,output)=subprocess.getstatusoutput("sensors | grep -i fan2")
        rpm1 = output.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        time.sleep(1)
        (status,output)=subprocess.getstatusoutput("sensors | grep -i fan2")
        rpm2 = output.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        time.sleep(1)
        (status,output)=subprocess.getstatusoutput("sensors | grep -i fan2")
        rpm3 = output.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        rpm = max(int(rpm1),int(rpm2),int(rpm3))
        average_rpm = int((int(rpm1)+int(rpm2)+int(rpm3)) / 3)
        print("average_rpm",average_rpm)
        print(give_rpm, rpm)
        if int(rpm) != 0:
            if one_data_fan == 0:
                if int(old_average_rpm) < int(average_rpm):
                    test.append({give_rpm:rpm})                                                                                                                                                                                                                                     
                else:
                    effective_rpm = int(rpm)
                    effective_handler = give_rpm
                    one_data_fan = 1
                    break

            old_rpm=rpm
            old_average_rpm = average_rpm
        else:
            pass

        max_rpm = rpm

    if int(effective_handler) > 100:
        with open('coolers.json', "w+") as file:
            file.seek(0)
            file.write(json.dumps(test))
            file.truncate()
        response = requests.post('http://ggc.center:8000/recalibrationOff/', data = {'id_rig': id_rig,
                                                                'effective_rpm':int(effective_rpm),
                                                                 'max_rpm':int(max_rpm),
                                                                 'effective_echo':effective_handler
                                                                 })
    else:
        send_mess(' RECALIBRATION is not accurate, try again.', id_rig)
        print("РЕКАЛИБРОВКА с шагом 5 пройти не удалось, пробую 10")
        os.system("rm /run/hive/fan_controller_recallibrate_req")
        testFan(id_rig, 10)

    print("РЕЗУЛЬТАТ РЕКАЛИБРОВКИ  >>  ", test)


    try:
        os.system("/hive/bin/miner start")
    except Exception:
        pass
    os.system("rm /run/hive/fan_controller_recallibrate_req")
    return("Maximum speed of external coolers :"+str(max_rpm))

if __name__ == '__main__':
    testFan(id_rig, 8)
