import sensors
import subprocess
sensors.init()

def test():
    labels = ''
    rpm_fun_gpu = {}

    for chip in sensors.iter_detected_chips():                         
        if 'amd' in str(chip) and str(chip) not in labels:
            labels += ' ' + str(chip)
            numGpu = numGpu+1                                                                                                                                              
            for feature in chip:
                if str(feature.label) == "fan1": 
                    try:
                        rpm_fun_gpu[str(numGpu)] = round(feature.get_value())
                    except Exception:
                        rpm_fun_gpu[str(numGpu)] = 0




#    (status,output_fan)=subprocess.getstatusoutput("nvidia-smi -q | grep 'Fan'")
#    green_fan = output_fan.replace('Fan Speed', '').replace(' ', '').replace(':', '').replace('%', ',').replace('\n', ',').split(',')
#    for fan in green_fan:
#        if len(str(fan)) != 0:
#            numGpu = numGpu+1
#            rpm_fun_gpu[str(numGpu)] = round(int(3600 / 100 * int(fan)))

    print(rpm_fun_gpu)

if __name__ == '__main__':
    test()
