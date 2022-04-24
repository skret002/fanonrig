import os, json                                                                                                                             
import time                                                                                                                           
import requests                                                                                                                                                                                                                                             
import subprocess

def testFan(id_rig):   

    subprocess.getstatusoutput("/hive/bin/miner stop")                                                                                                                                                                                                                                                      
    effective_rpm = 0                                                                                                                                                                                                                                                         
    effective_handler = 0
    max_rpm = 0                                                                                                                                                                                                                                                               
    one_data_fan = 0                                                                                                                                                                                                                                                          
    print("НАЧИНАЮ РЕКОЛЕБРОВКУ КУЛЕРОВ")
    os.system("echo 1 >> /sys/class/hwmon/hwmon1/pwm2_enable")
    os.system("echo 0  >> /sys/class/hwmon/hwmon1/pwm2")
    time.sleep(30)        # убираем остаточное движение если до этого были раскручены                                                                                                                                                                                                                                                     
    old_rpm =  0   

    for i in range(1, 60):
        give_rpm = i*5                                                                                                                               
        print(give_rpm)                                                                                                                              
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
        
        if int(rpm) != 0:
            if one_data_fan == 0:
                if int(old_rpm) < int(rpm):
                    pass                                                                                                                                                                                                                                     
                else:
                    effective_rpm = int(rpm)
                    effective_handler = give_rpm
                    one_data_fan = 1
                    break

            old_rpm=rpm
        else:
            pass

        max_rpm = rpm

    response = requests.post('http://ggc.center:8000/recalibrationOff/', data = {'id_rig': id_rig,
                                                                'effective_rpm':int(effective_rpm),
                                                                 'max_rpm':int(max_rpm),
                                                                 'effective_echo':effective_handler
                                                                 })
    const = {'const': int(effective_rpm)}

    with open('settings.json', "r+") as file:
        data = json.load(file)
        try:
           data["const"]  =  int(effective_rpm)
        except Exception:
            data.append(const)
        for i in range(0, 100):
            try:
                del data["minf"+str(i)]
            except Exception:
                pass
        file.seek(0)
        file.write(json.dumps(data))
        file.truncate()

    try:
        subprocess.getstatusoutput("/hive/bin/miner start")
        subprocess.getstatusoutput("/hive/bin/miner start", shell=True)
        subprocess.getstatusoutput("/hive/bin/miner start", shell=False)
    except Exception:
        os.system("/hive/bin/miner start")
    return("Maximum speed of external coolers :"+str(max_rpm))

if __name__ == '__main__':
    testFan()
    os.system("reboot")
    subprocess.run('reboot',shell=True)
