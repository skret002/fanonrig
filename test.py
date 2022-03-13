import sensors
sensors.init()

def test():
    labels = ''
    for chip in sensors.iter_detected_chips():                                                                                 
        if 'amdgpu' in str(chip) and str(chip) not in labels: 
            labels += ' ' + str(chip)                                                                                
            for feature in chip:

                print(feature)
                #if feature.label:

                #    if str(feature.label) == "edge":  
                #        try:                      
                #            if int(feature.get_value()) == 511:
                #                error511()                                                                        
                #            temp_gpu.append(round(int(feature.get_value())))                                                                         
                #        except Exception:
                #            temp_gpu.append(0)
                #        if str(feature.label) == '511':
                #            error511()

    #добавляем данные температуры с карт AMD если они есть
    #labels = ''
    #numGpu=-1
    #for chip in sensors.iter_detected_chips():                         
    #    if 'amd' in str(chip) and str(chip) not in labels:
    #        labels += ' ' + str(chip)
    #        numGpu = numGpu+1                                                                                                                                              
    #        for feature in chip:
    #            if str(feature.label) == "fan1": 
    #                try:
    #                    rpm_fun_gpu[str(numGpu)] = round(feature.get_value())
    #                except Exception:
    #                    rpm_fun_gpu[str(numGpu)] = 0

if __name__ == '__main__':
    test()