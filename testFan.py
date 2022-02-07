import sensors                                                                                                                        
import os                                                                                                                             
import time    
import requests                                                                                                                       
sensors.init()

def testFan(id_rig):            
    effective_rpm = 5200
    effective_handler = 160
    max_rpm = 5500
    print("начинаю РЕКОЛЕБРОВКУ КУЛЕРОВ")                                                                                             
    #os.system("echo 1 >>/sys/class/hwmon/hwmon1/pwm2_enable")                                                                         
    #os.system("echo 0  >> /sys/class/hwmon/hwmon1/pwm2")                                                                              
    time.sleep(5)                                                                                                                     
    old_rpm = 1000                                                                                                                    
    #for i in range(1,50):                                                                                                             
    #    give_rpm = i*5                                                                                                                
    #    os.system("echo " + str(give_rpm) +" >> /sys/class/hwmon/hwmon1/pwm2")                                                        
    #    print("echo " + str(give_rpm) +" >> /sys/class/hwmon/hwmon1/pwm2")                                                            
    #    time.sleep(3)                                                                                                                 
    #    for chip in sensors.iter_detected_chips():                                                                                    
    #        if str(chip) == "nct6779-isa-0a30" :                                                                                      
    #            for feature in chip:                                                                                                 
    #                if str(feature.label) == "fan2":                                                                                 
    #                    print("скорость внешних кулеров  ",feature.get_value())                                                       
    #                    if int(old_rpm) +20 >= int(feature.get_value()):                                                              
    #                        print("кулера эффективны до "+ str(give_rpm))                                                             
    #                        effective_rpm = feature.get_value()
    #                        effective_handler = give_rpm
    #                    old_rpm=feature.get_value()
    #    max_rpm = old_rpm
    response = requests.post('http://ggc.center:8000/recalibrationOff/', data = {'id_rig': id_rig, 
                                                                'effective_rpm':effective_rpm,
                                                                 'max_rpm':max_rpm,
                                                                 'effective_echo':effective_handler
                                                                 })
    print(response)

    return()
if __name__ == '__main__':
    testFan()
