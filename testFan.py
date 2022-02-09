import sensors                                                                                                                        
import os                                                                                                                             
import time    
import requests                                                                                                                       
sensors.init()

def testFan(id_rig):            
    numGpu=0
    for chip in sensors.iter_detected_chips():      
        numGpu = numGpu+1                   
        if 'amd' in str(chip):
            print(chip)                                                              
        #if str(chip.adapter_name) == "PCI adapter":                                                                                   
        #    for feature in chip:
        #        try:                                                                                                                                                                                           
        #            if str(feature.label) == "edge":                                                                                             
        #                #print(feature.get_value())     # температура
        #                temp_gpu.append(round(feature.get_value()))
        #        except Exception:
        #            print("Ошибка получения Температуры AMD")
        #            numGpu -1
        #        try:
        #            if str(feature.label) == "fan1": 
        #                #print(feature.get_value())    # скорость кулеров
        #                #rpm_fun_gpu.append({str(numGpu):feature.get_value()})

        #                rpm_fun_gpu[str(numGpu)] = feature.get_value()
        #        except Exception:
        #            print("Ошибка получения кулера AMD")

    return()
if __name__ == '__main__':
    testFan()
