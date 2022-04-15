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

     #ищем температуру на зеленых  картах   
    try:         
        (status,output)=subprocess.getstatusoutput("nvidia-smi -q | grep 'Memory Current Temp'")
        green_memory_temp = output.replace('Memory Current Temp', '').replace(':', '').replace(' ', '').replace('C', ',').replace('\n38', ',').split(',')
        print('::::::::::green_memory_temp::::::::::', green_memory_temp)
        for i in green_memory_temp:
            if len(str(i)) != 0:
                mem_temp.append(int(i))    
    except Exception as e:
        print("!!!!!!!!!!!!!ошибка в получении данных температуры памяти NVIDIA!!!!!!!!!!!!!")
        
    return(max(mem_temp))                                                                                                                            

if __name__ == '__main__':                                                                                                                           
    mem_temp()                                                                                                                                       
