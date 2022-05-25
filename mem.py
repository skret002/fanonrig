import sensors, json, subprocess                                                                                                                                       
sensors.init()                                                                                                                                                                                                                                                                          

def mem_temp():                                                                                                                                      
    mem_temp = []
    #ищем температуру памяти   - только hiveOS           
    try:  
        (status,output)=subprocess.getstatusoutput("cat /run/hive/fan_controller_req")     
        a =  json.loads(output)
        for memt in a["gpu_mtemp"]:
            mem_temp.append(int(memt))
    except Exception as e:   # если ошибка найдет только AMD
        mem_temp = []
        for chip in sensors.iter_detected_chips():                                                                                                       
            for feature in chip:                                                                                                                         
                if str(feature.label) == "mem":   
                    try:                                                                                                       
                        mem_temp.append(feature.get_value()) 
                    except Exception:
                        mem_temp.append(0)  

     #ищем температуру на зеленых  картах   

    return(max(mem_temp))                                                                                                                            

if __name__ == '__main__':                                                                                                                           
    mem_temp()                                                                                                                                       
