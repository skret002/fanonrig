import os
import subprocess
import requests

import sensors
sensors.init()

def get_temp():
    temp_gpu = []
    labels = ''
    try:
        for chip in sensors.iter_detected_chips():                                                                                
            if 'amdgpu' in str(chip) and str(chip) not in labels: 
                labels += ' ' + str(chip)                                                                                
                for feature in chip:
                    if feature.label:
                        if str(feature.label) == "edge":  
                            try:                                                                                            
                                temp_gpu.append(round(int(feature.get_value())))                                                                         
                            except Exception:
                                temp_gpu.append(0)
    except Exception:
        pass

    try:
        #добавляем данные температуры с карт nvidia если они есть
        (status,output)=subprocess.getstatusoutput("nvidia-smi -q | grep 'GPU Current Temp'")
        green_gpu_temp = output.replace('GPU Current Temp', '').replace(':', '').replace(' ', '').replace('C', ',').replace('\n38', ',').split(',')
        #print('green_gpu_temp', green_gpu_temp)
        for i in green_gpu_temp:
            if len(str(i)) != 0:
                temp_gpu.append(int(i))
    except Exception:
        pass

    hot_gpu = max(temp_gpu)
    print(hot_gpu)
    if int(hot_gpu) > 0:
        return(True)     
    else:
        return(False)


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