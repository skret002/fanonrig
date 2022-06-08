import os, json, requests, time, subprocess                                                                                                                    
from handler_messeges import transmit_mess as send_mess

answer_recallibrate ='/run/hive/fan_controller_recallibrate_rsp' # вывести рез. реколиб. текстом

def testFan(id_rig, step=4):   
    ## сначала стопарим майнер и удаляем старый файл рекалиброки
    subprocess.getstatusoutput("/hive/bin/miner stop") 
    try:
        subprocess.getstatusoutput("rm coolers.json")     
    except Exception:
        pass
    step = step +1
    effective_rpm = 0                                                                                                                                                                                                                                                         
    effective_handler = 0
    max_rpm = 0                                                                                                                                                                                                                                                               
    one_data_fan = 0                                                                                                                                                                                                                                                          
    print("**** STARTING COOLER REVOLUTION ****")
    subprocess.getstatusoutput("echo 1 >> /sys/class/hwmon/hwmon1/pwm2_enable")
    subprocess.getstatusoutput("echo 1  >> /sys/class/hwmon/hwmon1/pwm2")
    time.sleep(30)        # убираем остаточное движение если до этого были раскручены                                                                                                                                                                                                                                                     
    old_rpm =  0   
    old_average_rpm = 0
    test = []

    for i in range(0, 75):
        give_rpm = i*int(step)                                                                                                                                                                                                                                                           
        subprocess.getstatusoutput("echo " + str(give_rpm) +" >> /sys/class/hwmon/hwmon1/pwm2")
        time.sleep(9)                                                                                                                                
        (status,output1)=subprocess.getstatusoutput("sensors | grep -i fan2")
        rpm1 = output1.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        (status,output2)=subprocess.getstatusoutput("sensors | grep -i fan2")
        rpm2 = output2.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        (status,output3)=subprocess.getstatusoutput("sensors | grep -i fan2")
        rpm3 = output3.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        (status,output4)=subprocess.getstatusoutput("sensors | grep -i fan2")
        time.sleep(1)
        rpm4 = output4.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        (status,output5)=subprocess.getstatusoutput("sensors | grep -i fan2")
        rpm5 = output5.replace('fan2:', '').replace('RPM', '').replace('(min = 0 RPM)', '').replace(' ', '').replace('(min=0)','')
        rpm = max(int(rpm1),int(rpm2),int(rpm3),int(rpm4),int(rpm5))
        average_rpm = int((int(rpm1)+int(rpm2)+int(rpm3)+int(rpm4)+int(rpm5)) / 5)
        print("average_rpm - ",average_rpm)
        if int(rpm) != 0:
            if one_data_fan == 0:
                if int(old_average_rpm) < int(average_rpm):
                    test.append({give_rpm:average_rpm})                                                                                                                                                                                                                                     
                else:
                    effective_rpm = int(average_rpm)
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
        try:
            os.system("/hive/bin/miner start")
        except Exception:
            pass
        try:
            os.system("rm /run/hive/fan_controller_recallibrate_req")
        except Exception:
            pass
        file_info1 = open(answer_recallibrate, "w+")                                                                                              
        file_info1.write('device_name: '+ str("Recalibration completed successfully.The effective speed of your box's coolers > " +str(max_rpm) ))
        file_info1.close()
        return("Maximum speed of external coolers :"+str(max_rpm))
    else:
        send_mess(' RECALIBRATION is not accurate, try again.', id_rig)
        file_info1 = open(answer_recallibrate, "w+")                                                                                              
        file_info1.write('device_name: '+ str('Recalibration with standard parameters failed. I will try other modes, the result will be sent to > ggc.center'))
        file_info1.close() 
        print("!!!! RECALIBRATION with step 5 failed, I try !!!!", step+1)
        testFan(id_rig, step)

    print("**** RESULT OF RECALIBRATION  **** >>  ", test)

if __name__ == '__main__':
    testFan(id_rig, 8)
