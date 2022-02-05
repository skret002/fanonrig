import sensors
import os
sensors.init()

def testFan():
    print("начинаю РЕКОЛЕБРОВКУ КУЛЕРОВ")
    os.system("echo 1 >>/sys/class/hwmon/hwmon1/pwm2_enable")
    old_rpm = 0
    for i in range(0,17)
        give_rpm = 15*i
        os.system("echo" + int(give_rpm) +" >> /sys/class/hwmon/hwmon1/pwm2")
        for chip in sensors.iter_detected_chips():
            if str(chip) == "nct6779-isa-0a30" :
                for feature in chip:                                                                                                      
                    if str(feature.label) == "fan2":                                                                                      
                        print("скорость внешних кулеров  ",feature.get_value())
                        if int(old_rpm) < int(feature.get_value()) - 400
                            print("на этом все, кулера говно")
                        old_rpm = feature.get_value()
