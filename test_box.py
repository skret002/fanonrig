import os
import subprocess
import requests
import sensors
sensors.init()

def testing():
    # начинаю тест железа
    global rpmfun
    temp_gpu = []
    rpm_fun_gpu = []
    for chip in sensors.iter_detected_chips():
        if str(chip) == "nct6779-isa-0a30" :
            for feature in chip:                                                                                                      
                if str(feature.label) == "fan2":                                                                                      
                    #print("скорость внешних кулеров  ",feature.get_value())
                    rpmfun = feature.get_value()
    if rpmfun != 0:
        pass
        #print("внешние кулера управляемые и крутятся")
    else:
        print("Внешних кулеров нет или они не управляемые")
        time.sleep(10)
        testing()
        return("There are no external coolers or they are not controlled, check the connections of the coolers to the motherboard. Make sure you are using WIND TANK TECHNOLOGIES L.L.C box")
    try:
        get_temp()
    except Exception:
        return("Data about video cards cannot be read, GPU may not be installed")

    print("тест завершился успешно")
    return(True)