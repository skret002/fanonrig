import sensors                                                                                                                                       
sensors.init()                                                                                                                                       
import subprocess                                                                                                                                    

def mem_temp():                                                                                                                                      
    mem_temp = []
    #ищем температуру на красных картах                                                                                                                  
    for chip in sensors.iter_detected_chips():                                                                                                       
        for feature in chip:                                                                                                                         
            if str(feature.label) == "mem":   
                try:                                                                                                       
                    mem_temp.append(feature.get_value()) 
                except Exception:
                    mem_temp.append(0)                                                                                                                           
    return(max(mem_temp))                                                                                                                            

if __name__ == '__main__':                                                                                                                           
    mem_temp()                                                                                                                                       
