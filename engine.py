import json #подключили библиотеку для работы с json
import simplejson
from pprint import pprint #подключили Pprint для красоты выдачи текста
from testFan import testFan
from handler_messeges import transmit_mess as send_mess
import os
import subprocess
import requests
import time
import sys
import glob
import sensors
sensors.init()

rigOnBoot = 0
old_selected_mod = 0
selected_mod = 0
terget_temp_min = 0
terget_temp_max = 0
min_fan_rpm = 0
hot_gpu = 0
old_hot_gpu =0
critical_temp = 0
const_rpm = 0
last_rpm = 0
select_fan = 0
boost = 0
rigRpmFanMaximum = 0
rigRpmFaneffective = 0
rpmfun= 0
option1 = {}
option2 = 0
id_rig_in_server = 0
statusAlertSystem = False
gpuFanSetHive = 0
typeGpu = 0
ressetRig=True
stable_temp_round = 0
optimum_fan = 0
optimum_temp = 0
optimum_on = 0
optimun_echo = 0
key_slave = ''

def error511():
    send_mess(' Замечена ошибка 511, проверьте блок питания и прилигание охлаждения к GPU.', id_rig_in_server)

def active_cool_mod():
    global last_rpm
    global boost
    global min_fan_rpm
    global stable_temp_round
    global optimum_fan
    global old_hot_gpu
    global hot_gpu
    global optimum_temp
    global optimum_on
    global optimun_echo
    print("ПОРОГ ВКЛЮЧЕНИЯ ОПЕРЕЖЕНИЯ",int(hot_gpu) >= int(terget_temp_min) + int(int(terget_temp_max - terget_temp_min)/2) + 2,int(terget_temp_min) + int(int(terget_temp_max - terget_temp_min)/2) + 2)
    print("stable_temp_round",stable_temp_round)
    print("optimum_on",optimum_on)

    if int(hot_gpu) >= int(terget_temp_min) and int(hot_gpu) < int(critical_temp):
        corect_boost = (int(const_rpm) / int(terget_temp_max - terget_temp_min)) * ((int(hot_gpu) - int(terget_temp_min))) + int(boost)
        
        if int(hot_gpu) >= int(terget_temp_min) + int(int(terget_temp_max - terget_temp_min)/2) + 2:
            last_rpm = int(corect_boost)
            print("///// АКТИВИРОВАН РЕЖИМ С ОПЕРЕЖЕНИЕМ", int(last_rpm))
            os.system("echo " + str(int(last_rpm)) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
            old_hot_gpu = hot_gpu
            stable_temp_round = 0
            optimum_on = 0
        else:
            if optimum_on == 0 and stable_temp_round <= 20:
                last_rpm = (int(const_rpm) / int(terget_temp_max - terget_temp_min)) * ((int(hot_gpu) - int(terget_temp_min)))
                os.system("echo " + str(int(last_rpm)) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
                stable_temp_round = stable_temp_round + 1
                print("///// АКТИВИРОВАН УСРЕДНЕНЫЙ РЕЖИМ", int(last_rpm), stable_temp_round)
                time.sleep(10) 

            
            if  optimum_on == 1 and int(hot_gpu) < int(terget_temp_min) + int(int(terget_temp_max - terget_temp_min)/2) +1:
                print("///////////////////////////////Применяю оптимум//////////////////////",optimun_echo)
                print(optimun_echo)
                os.system("echo " + str(int(optimun_echo)) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
                time.sleep(30)
                if old_hot_gpu < hot_gpu:
                    optimum_on = 0
                    stable_temp_round = 0
                else:
                    old_hot_gpu = hot_gpu

            
            if stable_temp_round > 20 and optimum_on == 0 :
                print("/////Температура стабильна, ищу оптимум ///")
                corect_boost = int(corect_boost) - int(boost)
                optimum_fan = optimum_fan + round(int(const_rpm) / 100)
                last_rpm = int(corect_boost) - int(optimum_fan)
                print("значения после корекции", last_rpm)
                os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan)) 
                time.sleep(30)   
                old_hot_gpu = hot_gpu
                if int(optimum_temp) == int(hot_gpu):
                    optimum_on = 1
                    print("ОПТИМУМ ГОТОВ", optimun_echo)
                    old_hot_gpu = hot_gpu
                else:
                    optimum_temp = hot_gpu + 1
                    optimun_echo = last_rpm

    
    if hot_gpu < terget_temp_min - 4:
        last_rpm = int(min_fan_rpm)
        os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        #print("температура сильно ниже таргета, даю  ",last_rpm)
        #print(hot_gpu)

    if hot_gpu < terget_temp_min -2 and hot_gpu < terget_temp_min -3:
        last_rpm = round(const_rpm / 10)
        os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        #print("Температуры сильно ниже таргета ",last_rpm)

    if hot_gpu < terget_temp_min -2:
        last_rpm = round(const_rpm / 100 * 15)
        os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        #print("температура ниже уровня, даю ",last_rpm)

    if hot_gpu == terget_temp_min - 2:
        last_rpm = int(const_rpm / 100 * 20)
        os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        #print("температура ниже уровня но подходит к уровню удержания, даю ",last_rpm)
    
    if hot_gpu == terget_temp_min - 1:
        last_rpm = int(const_rpm / 100 * 25)
        os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        #print("температура впритык к началу таргета ",last_rpm)
        #print(hot_gpu)

    if hot_gpu >= critical_temp:
        os.system("echo 250 >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        #print("температура критическая, выполняю защитный алгоритм!")
        send_mess(' Температура достигла критического значения, вынужден остановить майнер', id_rig_in_server)
        os.system("miner stop")
        time.sleep(7)
        os.system("miner stop")
        #print("майнер остановлен")

    if hot_gpu >= critical_temp +5 :
        os.system("echo 250 >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        print("температура выше критической на 5 , выполняю защитный алгоритм!")
        send_mess(' Температура карты привышает критическую, выключаю риг', id_rig_in_server)
        os.system("sreboot shutdown")

def addFanData(rpmfun, temp_gpu0,temp_gpu1,temp_gpu2,temp_gpu3,temp_gpu4,temp_gpu5,temp_gpu6,temp_gpu7,rpm_fun_gpu, alertFan,problemNumberGpu, hot_gpu):
    #print('ЗАШЛИ В ВЫДАЧУ ДАННЫХ О КУЛЕРАХ')
    data={"id_in_serv": id_rig_in_server,'rpmfun':rpmfun,
                            'temp_gpu0':temp_gpu0, 'temp_gpu1':temp_gpu1,
                            'temp_gpu2':temp_gpu2,'temp_gpu3':temp_gpu3,
                            'temp_gpu4':temp_gpu4,'temp_gpu5':temp_gpu5,
                            'temp_gpu6':temp_gpu6,'temp_gpu7':temp_gpu7,
                            'rpm_fun_gpu':rpm_fun_gpu,
                            'alertFan':alertFan, 'problemNumberGpu':problemNumberGpu,
                            'hot_gpu':hot_gpu
                            }
    r = requests.post("http://ggc.center:8000/add_and_read_fandata/", data=data)
	#print(response.json())
	#response = response.json()

def get_temp():
    global rpmfun
    global hot_gpu
    temp_gpu = []
    rpm_fun_gpu = {}
    alertFan = False
    problemNumberGpu = None
    numGpu=0

    #try:
    labels = ''
    for chip in sensors.iter_detected_chips():
        numGpu = numGpu+1                                                                                  
        if 'amdgpu' in str(chip) and str(chip) not in labels: 
            labels += ' ' + str(chip)                                                                                
            for feature in chip:
                if feature.label:
                    if str(feature.label) == "edge":                                                                                            
                        temp_gpu.append(round(int(feature.get_value())))
                        if int(feature.label) == -511:
                            error511()


    labels = ''
    numGpu=-1
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
    #добавляем данные температуры с карт nvidia если они есть
    (status,output)=subprocess.getstatusoutput("nvidia-smi -q | grep 'GPU Current Temp'")
    green_gpu_temp = output.replace('GPU Current Temp', '').replace(':', '').replace(' ', '').replace('C', ',').replace('\n38', ',').split(',')
    #print('green_gpu_temp', green_gpu_temp)
    for i in green_gpu_temp:
        if len(str(i)) != 0:
            temp_gpu.append(int(i))
            if int(i) == -511:
                error511()

    #добавляем данные кулеров с карт nvidia если они есть
    (status,output_fan)=subprocess.getstatusoutput("nvidia-smi -q | grep 'Fan'")
    green_fan = output_fan.replace('Fan Speed', '').replace(' ', '').replace(':', '').replace('%', ',').replace('\n', ',').split(',')
    for fan in green_fan:
        if len(str(fan)) != 0:
            numGpu = numGpu+1
            rpm_fun_gpu[str(numGpu)] = round(int(3600 / 100 * int(fan)))

    #print("Найдено карт", len(temp_gpu)) #вывели результат на экран
    #print("rpm_fun_gpu",rpm_fun_gpu)
    #print("temp_gpu",temp_gpu)
    hot_gpu = max(temp_gpu)
    #print("Самая горячая карта", max(temp_gpu)) #вывели результат на экран
    #print("самая высокая скорость кулера видеокарты!", rpm_fun_gpu[max(rpm_fun_gpu, key=rpm_fun_gpu.get)]) #вывели результат на экран
    #print("!!!",statusAlertSystem == True, gpuFanSetHive == 1, typeGpu == 0)
    try:
        if statusAlertSystem == True and gpuFanSetHive == 1 and typeGpu == 0:
            #print("зашли в проверку кулеров",rpm_fun_gpu[max(rpm_fun_gpu, key=rpm_fun_gpu.get)] - rpm_fun_gpu[max(rpm_fun_gpu, key=rpm_fun_gpu.get)]/5, rpm_fun_gpu[min(rpm_fun_gpu, key=rpm_fun_gpu.get)])
            if rpm_fun_gpu[max(rpm_fun_gpu, key=rpm_fun_gpu.get)] - rpm_fun_gpu[max(rpm_fun_gpu, key=rpm_fun_gpu.get)]/10 > rpm_fun_gpu[min(rpm_fun_gpu, key=rpm_fun_gpu.get)]:
                #print("обнаружена проблема с кулерами")
                alertFan = True
                problemNumberGpu = min(rpm_fun_gpu, key=rpm_fun_gpu.get)
                #print(problemNumberGpu)
            else:
                alertFan = False
                problemNumberGpu = None
        else:
            alertFan = False
    except Exception:
        pass
    try:
        temp_gpu0 = temp_gpu[0]
    except Exception:
        temp_gpu0 = 0
    try:
        temp_gpu1 = temp_gpu[1]
    except Exception:
        temp_gpu1 = 0
    try:
        temp_gpu2 = temp_gpu[2]
    except Exception:
        temp_gpu2 = 0
    try:
        temp_gpu3 = temp_gpu[3]
    except Exception:
        temp_gpu3 = 0
    try:
        temp_gpu4 = temp_gpu[4]
    except Exception:
        temp_gpu4 = 0
    try:
        temp_gpu5 = temp_gpu[5]
    except Exception:
        temp_gpu5 = 0
    try:
        temp_gpu6 = temp_gpu[6]
    except Exception:
        temp_gpu6 = 0
    try:
        temp_gpu7 = temp_gpu[7]
    except Exception:
        temp_gpu7 = 0
    #except Exception:
    #    pass
    ##   time.sleep(3)

    for chip in sensors.iter_detected_chips():
        if str(chip) == "nct6779-isa-0a30" :
            for feature in chip:                                                                                                      
                if str(feature.label) == "fan2":                                                         
                    #print("скорость внешних кулеров  ", feature.get_value())
                    if len(str(int(feature.get_value()))) !=0 or len(str(int(feature.get_value()))) != None:
                        rpmfun = int(feature.get_value())
                    else:
                       rpmfun = 0
    addFanData(rpmfun,temp_gpu0,temp_gpu1,temp_gpu2,temp_gpu3,temp_gpu4,temp_gpu5,temp_gpu6,temp_gpu7, rpm_fun_gpu, alertFan,problemNumberGpu,hot_gpu)
    time.sleep(20)

def testing():
    print("начинаю тест железа")
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
        #print("внешних кулеров нет или они не управляемые")
        sys.exit()
    for chip in sensors.iter_detected_chips():                                                                                        
        if str(chip.adapter_name) == "PCI adapter":                                                                                   
            for feature in chip:                                                                                                      
                try:                                                                                                                  
                    if str(feature.label) == "edge":                                                                                  
                        #print(feature.get_value())     # температура
                        temp_gpu.append(feature.get_value())
                    if str(feature.label) == "fan1": 
                        #print(feature.get_value())    # скорость кулеров
                        rpm_fun_gpu.append(feature.get_value())
                except Exception as e:                                                                                                
                    pass
    if len(temp_gpu) != 0:
        pass
    	#print("обнаружено ",len(temp_gpu), "карт" )
    	#print(temp_gpu)
    	#print(rpm_fun_gpu)
    else:
    	print("видеокарт не обнаружено, сорян")
    	sys.exit()
    print("тест завершился успешно")

def test_key(rig_id='', rig_name=''):                                                                                                 
    print("Зашли в test_key", len(str(rig_id)))                                                                                       
    global key_slave                                                                                                                  
    r_id = ""                                                                                                                         
    r_name = ""                                                                                                                       
    for filename in glob.iglob('/hive-config/*.key_slave', recursive=True):                                                           
        file_key = open(filename, "r")
        key_slave = file_key.read()                                                                                                   
    print('key_slave',key_slave)                                                                                                      
    file1 = open("/hive-config/rig.conf", "r")                                                                                        
    lines = file1.readlines()  

    for line in lines:                                                                                                                
        if "WORKER_NAME=" in line:                                                                                                    
            r_name = line.replace("WORKER_NAME=", "").replace('"', '').replace('\n', '')                                              
            print(r_name)                                                                                                             
    for line in lines:                                                                                                                
        if "RIG_ID" in line.split('='):
            r_id = line.replace("RIG_ID=", "").replace('\n', '')                                                                      
            print(r_id)                                                                                                               
    if len(str(rig_id)) != 0 and rig_name != r_name and rig_name != '':                                                               
        print("///// изменилось имя рига ///////")
        with open('settings.json', 'r+') as f:                                                                                        
            json_data = json.load(f)                                                                                                  
            json_data['rig_name'] = str(r_name)
            f.seek(0)                                                                                                                 
            f.write(json.dumps(json_data))                                                                                            
            f.truncate()                                                                                                              
        os.system("sreboot")

            
    if len(str(rig_id)) == 0:                                                                                                         
        print("Это первый запуск, прописываю ID в память")                                                                            
        with open('settings.json', 'r+') as f:
            json_data = json.load(f)                                                                                                  
            json_data['rig_id'] = str(r_id)                                                                                           
            json_data['rig_name'] = str(r_name)                                                                                       
            f.seek(0)                                                                                                                 
            f.write(json.dumps(json_data))                                                                                            
            f.truncate()                                                                                                              
       # os.system("sreboot")   

    if str(rig_id) == str(r_id):
        print("Защита пройдена и в этот раз я не сотру систему")
    return()

def get_setting_server(id_rig_in_server):
    #print(id_rig_in_server)
    response = requests.get('http://ggc.center:8000/get_option_rig/', data = [('id_in_serv', id_rig_in_server)] )
    #print(response)
    response = response.json()
    #print('get_setting_server',response["data"][0]["attributes"])
    global selected_mod
    global terget_temp_min
    global terget_temp_max
    global min_fan_rpm
    global select_fan
    global boost
    global critical_temp
    global option1
    global statusAlertSystem
    global gpuFanSetHive
    global typeGpu
    global const_rpm
    global rigOnBoot
    if const_rpm == 0:
        #print("первое получение данных")
        const_rpm = int(response["data"][0]["attributes"]["effective_echo_fan"])
        typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])
        gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])
        statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]
        selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
        terget_temp_min = int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_min"])
        terget_temp_max = int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_max"])
        min_fan_rpm = round(const_rpm / 100 * int(response["data"][0]["attributes"]["SetMode0"]["min_fan_rpm"]))
        select_fan = int(response["data"][0]["attributes"]["SetModeFan"]["select_fan"])
        critical_temp = int(response["data"][0]["attributes"]["SetMode0"]["critical_temp"])
        boost=int(response["data"][0]["attributes"]["SetMode0"]["boost"])
        rigOnBoot = 1
    else:
        #print("Настройки изменены")
        if const_rpm != int(response["data"][0]["attributes"]["effective_echo_fan"]):
            const_rpm = int(response["data"][0]["attributes"]["effective_echo_fan"])
            engine_start()

        if typeGpu != int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"]):
            typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])
            engine_start()

        if gpuFanSetHive != int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"]):
            gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])
            engine_start()

        if statusAlertSystem != response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]:
            statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]
            engine_start()

        if selected_mod != int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"]):
            selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
            engine_start()

        if terget_temp_min != int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_min"]):
            terget_temp_min = int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_min"])
            engine_start()

        if terget_temp_max != int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_max"]):
            terget_temp_max = int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_max"])
            engine_start()

        if min_fan_rpm !=  round(const_rpm / 100 * int(response["data"][0]["attributes"]["SetMode0"]["min_fan_rpm"])):
            min_fan_rpm = round(const_rpm / 100 * int(response["data"][0]["attributes"]["SetMode0"]["min_fan_rpm"]))
            engine_start()

        if select_fan != int(response["data"][0]["attributes"]["SetModeFan"]["select_fan"]):
            select_fan = int(response["data"][0]["attributes"]["SetModeFan"]["select_fan"])
            engine_start()

        if critical_temp != int(response["data"][0]["attributes"]["SetMode0"]["critical_temp"]):
            critical_temp = int(response["data"][0]["attributes"]["SetMode0"]["critical_temp"])
            engine_start()

        if boost != int(response["data"][0]["attributes"]["SetMode0"]["boost"]):
            boost=int(response["data"][0]["attributes"]["SetMode0"]["boost"])
            engine_start()

    # проверяем включена ли реколебровка и если нужно запускаем
    if response["data"][0]["attributes"]["recalibrationFanRig"] == True:
        testFan(id_rig_in_server)
        get_setting_server(id_rig_in_server)
    return("true")

def get_setting_server1(id_rig_in_server):
    #print(id_rig_in_server)
    response = requests.get('http://ggc.center:8000/get_option_rig/', data = [('id_in_serv', id_rig_in_server)] )
    response = response.json()
    #print(response)
    global option1
    global selected_mod
    global statusAlertSystem
    global gpuFanSetHive
    global typeGpu
    global rigOnBoot
    if rigOnBoot ==0:
        typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])
        gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])
        statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]
        selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
        cache = response["data"][0]["attributes"]["SetMode1"]
        rigOnBoot =1
    else:
        if typeGpu != int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"]):
            typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])
            engine_start()

        if gpuFanSetHive != int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"]):
            gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])
            engine_start()

        if statusAlertSystem != response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]:
            statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]
            engine_start()

        if selected_mod != int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"]):
            selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
            engine_start()

        if cache != response["data"][0]["attributes"]["SetMode1"]:
            cache = response["data"][0]["attributes"]["SetMode1"]
            engine_start()


    del cache['id']
    for i in cache:
        key1 = i.replace('t', '')
        vals = cache[i].split(",")
        two_val = []
        for val in vals:
            two_val.append(int(val))
        #print(key1, two_val)
        option1.update({str(key1):two_val}) 

    #print(option1)
    return("true")
def get_setting_server2(id_rig_in_server):
    # передаем данные о риге и получаем ответ с id
    #print(id_rig_in_server)
    response = requests.get('http://ggc.center:8000/get_option_rig/', data = [('id_in_serv', id_rig_in_server)] )
    response = response.json()
    #print(response)
    global option2
    global selected_mod
    global statusAlertSystem
    global gpuFanSetHive
    global typeGpu
    global rigOnBoot

    if rigOnBoot ==0:
        typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])
        gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])
        statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]
        selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
        option2 = response["data"][0]["attributes"]["SetMode2"]["SetRpm"]
        rigOnBoot =1
    else:
        if typeGpu != int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"]):
            typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])
            engine_start()

        if gpuFanSetHive != int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"]):
            gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])
            engine_start()

        if statusAlertSystem != response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]:
            statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]
            engine_start()
 
        if selected_mod != int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"]):
            selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
            engine_start()

        if option2 != response["data"][0]["attributes"]["SetMode2"]["SetRpm"]:
            option2 = response["data"][0]["attributes"]["SetMode2"]["SetRpm"]
            engine_start()
    
    return("true")

def sendInfoRig(rig_id, rig_name, key_slave):
    global id_rig_in_server
    try:
        param= [('rigId', rig_id), ('rigName', rig_name), ('key_slave',key_slave)] 
        response = requests.post('http://ggc.center:8000/add_rig_or_test/', data = param )
        id_rig_in_server = response.json()["data"]
        #print('id_rig_in_server тут смотреть',id_rig_in_server)
    except Exception as e:
        print('ошибка в sendInfoRig', e)
        time.sleep(10)
        sendInfoRig(rig_id, rig_name, key_slave)
    return(True)

def test_select_mod():
	print(selected_mod, old_selected_mod)
	if selected_mod == old_selected_mod:
		pass
	else:
		engine_start()



def engine_start():
    global old_selected_mod
    global selected_mod
    global terget_temp_min
    global terget_temp_max
    global min_fan_rpm
    global hot_gpu
    global critical_temp
    global const_rpm
    global last_rpm
    global select_fan
    global boost
    global rpmfun
    global option1
    global option2
    global id_rig_in_server
    global ressetRig

    testing()

    with open('settings.json', 'r', encoding='utf-8') as f: #открыли файл с данными
        text = json.load(f)
    rig_id = str(text["rig_id"])
    rig_name = str(text["rig_name"])
    old_selected_mod = selected_mod
    test_key(rig_id, rig_name)
    
    # передаем данные о риге и получаем ответ с id
    sendInfoRig(rig_id,rig_name,key_slave)
    if ressetRig == True:
        requests.post("http://ggc.center:8000/ressetRigAndFanData/", data={'ressetRig':'True', 'id_rig_in_server':id_rig_in_server})
        ressetRig = False

    if get_setting_server(id_rig_in_server, 'key_slave':key_slave) == "true":
        pass
        #print("ответ с сервера получен")
    else:
        #print("нет ответа с сервера")
        os.system("sreboot")
  
    if selected_mod == 0:
        #print("Выбран режиж удержания температур в диапазоне" , terget_temp_min, terget_temp_max)
        #print("начинаю вычесления, а пока что продуем систему")
        send_mess(' Интеллектуальный режим активирован', id_rig_in_server)
        os.system("echo 1 >>/sys/class/hwmon/hwmon1/pwm"+str(select_fan)+"_enable")
        os.system("echo " + str(round(const_rpm / 100 * 50)) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        while 1 > 0:
            test_select_mod()
            time.sleep(1)
            get_setting_server(id_rig_in_server)
            get_temp()
            active_cool_mod()
    elif selected_mod == 1:
        print("Выбран ручной режим")
        send_mess(' Ручной режим активирован', id_rig_in_server)
        os.system("echo 1 >>/sys/class/hwmon/hwmon1/pwm"+str(select_fan)+"_enable")
        os.system("echo " + str(round(const_rpm / 100 * 50)) + ">> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        while 1 > 0:
            test_select_mod()
            time.sleep(7)
            get_temp()
            if get_setting_server1(id_rig_in_server) == "true":
                #print("ответ с сервера получен")
                test_select_mod()
            else:
                option1 = text["1"]	
            for i in option1:
                print(option1[i][0],option1[i][1])
                if hot_gpu >= option1[i][0] and  hot_gpu <= option1[i][1]:
                    last_rpm = round(int(const_rpm / 100) * int(i))
                    print("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
                    os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
                    print("выдаю  ",i,"%",  "горячая карта ", hot_gpu)
    elif selected_mod == 2:
        print("Выбран статичный режим")
        os.system("echo 1 >>/sys/class/hwmon/hwmon1/pwm"+str(select_fan)+"_enable")
        send_mess(' Статичный режим активирован', id_rig_in_server)
        while 1 > 0:
            time.sleep(10)
            if get_setting_server2(id_rig_in_server) == "true":
                print("ответ с сервера получен")
                get_temp()
                test_select_mod()
                option = round(const_rpm / 100 * int(option2))
                os.system("echo " + str(option2) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
                print("echo " + str(option2) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))

if __name__ == '__main__':
	try:
		engine_start()
	except Exception as e:
		print(e)
		engine_start()
	#get_temp()
