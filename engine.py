import glob, json, os, re, subprocess, sys, time, requests, sensors
from pprint import pprint  # подключили Pprint для красоты выдачи текста

from handler_messeges import transmit_mess as send_mess
from mem import mem_temp
from talk_from_hive import communication_hive
from test_pci import applay_pci_status, test
from testFan import testFan
from update_task import task_update

sensors.init()
# общие переменные
rigOnBoot = 0
old_selected_mod = 0
selected_mod = 0
terget_temp_min = 0
terget_temp_max = 0
min_fan_rpm = 0
target_mem_temp=88
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
soft_rev = ''
key_slave = ''
target_fan_opt_lock =0
start_optimum = 0 
mem_t = 0
temp_gpu_freeze = 0
old_stab_balance = 0
optimum_round = 0
rigRpmFanMaximum = 0
mod_option_hive = 0
min_fan_rpm_persent = None
device_name = ''
real_min_fan_rpm = 0
last_rpm_s = 0
boost_in_s =0
gpu_status = ''


def error511():
    send_mess(' Error 511 noticed, check the power supply and cooling connection to the GPU.', id_rig_in_server)

def active_cool_mod():                                                                                                                     
    global last_rpm, optimum_fan, boost, min_fan_rpm, stable_temp_round, optimum_fan, old_hot_gpu, hot_gpu, optimum_temp, optimum_on, optimun_echo, start_optimum, target_fan_opt_lock, mem_t, temp_gpu_freeze, old_stab_balance, optimum_round, last_rpm_s, boost_in_s

    optimum_temp = int(terget_temp_min) + int(int(terget_temp_max - terget_temp_min)/2)
    if int(boost) < 1:
        boost = 1
    try:
        mem_t = int(mem_temp())  
        if int(mem_t) >75:
            boost_mem = int((int(const_rpm) /100) * (mem_t - 75))
        else:
            boost_mem = 0
    except Exception:
        mem_t = 0
        boost_mem = 0

    if int(hot_gpu) >= int(critical_temp):
        subprocess.getstatusoutput("echo 300 >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        subprocess.run('/hive/bin/miner stop',shell=True)
        send_mess("MINER STOPPED, DANGEROUS TEMPERATURE " + str(hot_gpu), id_rig_in_server)

    if ((int(hot_gpu) >= int(terget_temp_min)+1) and (int(hot_gpu) < int(critical_temp))) or int(mem_t) >= int(target_mem_temp):
        if (int(hot_gpu) >= int(terget_temp_max) -2) or (int(mem_t) >= 110):   
            if int(mem_t) <= 90:    
                boost_mem =  0 
            elif (int(mem_t) > 90) and (int(mem_t) <= 95):
                boost_mem = round(int(boost_mem /2))               
            corect_boost = (int(const_rpm) / (int(terget_temp_max - terget_temp_min))) * ((int(hot_gpu) - int(terget_temp_min))) + int(boost)+ int(boost_mem)
            corect_boost = int(int(corect_boost/100)*90)
            print("///// АКТИВИРОВАН РЕЖИМ С ОПЕРЕЖЕНИЕМ", int(corect_boost))
            subprocess.getstatusoutput("echo " + str(int(corect_boost)) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
            old_hot_gpu = hot_gpu
            stable_temp_round = 0
            optimum_on = 0
            get_temp()
            time.sleep(15)
            return()
        else:    
            if (optimum_on == 0) and (stable_temp_round <= 15) and (int(mem_t) <110):
                if int(old_hot_gpu) != int(hot_gpu) or int(hot_gpu) > int(optimum_temp) or int(mem_t) > int(target_mem_temp):
                    print('усредненый пересчитываю') 
                    last_rpm = int((int(const_rpm) / (int(terget_temp_max - terget_temp_min))) * ((int(hot_gpu) - int(terget_temp_min)))) 
                    if int(hot_gpu) > int(optimum_temp) or int(mem_t) > int(target_mem_temp):
                        print('Применяю адаптивно-усредненый') 
                        last_rpm_s = (last_rpm/100)* (80 + (int(hot_gpu) - int(optimum_temp))*2)
                        if last_rpm_s < 0:
                            last_rpm_s = 0
                        last_rpm_s = int(last_rpm_s) + int(boost_mem) + int(boost) + int(boost_in_s)
                    else:
                        last_rpm_s = int(((int(last_rpm)/100)*80) + int(boost_mem) + int(boost) + int(boost_in_s))
                    if int(last_rpm_s) < int(real_min_fan_rpm): # ограничеваем минимальной скоростью
                        subprocess.getstatusoutput("echo " + str(int(real_min_fan_rpm)) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
                    else:
                        subprocess.getstatusoutput("echo " + str(int(last_rpm_s)) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
                        start_optimum = last_rpm_s
                        old_hot_gpu = hot_gpu
                        time.sleep(29)
                    get_temp()                                                                                       
                else:          
                    print('усредненый оставляю как есть')
                    get_temp()
                    old_hot_gpu = hot_gpu
                    time.sleep(29)
                if int(hot_gpu) <= int(optimum_temp) and int(mem_t) <= int(target_mem_temp):
                    stable_temp_round = stable_temp_round + 1 
                    time.sleep(29)
                    print("::::::::Все стабильно, готовлюсь к search optimum:::::::::", stable_temp_round)
                else:
                    boost_in_s = boost_in_s + int(int(int(const_rpm) / 100) * 2 )
                    #stable_temp_round = 0 
                    time.sleep(29)
                    print("::::::::сбросил stable_temp_round до входа search optimum:::::::::",boost_in_s, last_rpm_s)

            elif (stable_temp_round > 15) and (optimum_on == 0) and (int(mem_t) <= (int(target_mem_temp) + 2)):  
                print("/////Температура стабильна, ищу оптимум ///")
                get_temp()
                optimum_fan = optimum_fan + int(int(const_rpm) / 100) * 1                                                                 
                last_rpm = int(start_optimum) - int(optimum_fan)
                print("значения после корекции", last_rpm)
                #send_mess("/////Температура стабильна, ищу оптимум /// значения после корекции " + str(last_rpm) , id_rig_in_server)  
                if int(last_rpm) < int(real_min_fan_rpm):
                    last_rpm = int(real_min_fan_rpm)
                    optimum_on = 1
                    old_hot_gpu = hot_gpu
                    optimun_echo = last_rpm
                    temp_gpu_freeze = int(hot_gpu)
                subprocess.getstatusoutput("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
                time.sleep(29)
                #get_temp()
                old_hot_gpu = hot_gpu
                if int(hot_gpu) > int(optimum_temp):
                    stable_temp_round = 0     
                if  (int(mem_t) == int(target_mem_temp)) or (int(optimum_temp) == int(hot_gpu)) or (int(last_rpm) <= int(real_min_fan_rpm)):
                    print('optTRIGER', int(mem_t) == int(target_mem_temp) , int(optimum_temp) == int(hot_gpu),(int(last_rpm) <= int(real_min_fan_rpm)))
                    optimum_on = 1
                    print("ОПТИМУМ ГОТОВ", optimun_echo, 'mem_t', mem_t)
                    old_hot_gpu = hot_gpu
                    optimun_echo = last_rpm + int(int(int(const_rpm) / 100) * 5 )
                    temp_gpu_freeze = int(hot_gpu)
                return()
            elif optimum_on == 1:     
                print("///////////////////////////////Применяю оптимум//////////////////////")
                get_temp()
                stab_balance_mem= 0
                stab_balance = 0 
                #send_mess("оптимум - коректирую ", id_rig_in_server)
                stab_balance =    int((int(hot_gpu) - int(temp_gpu_freeze)) * ((int(const_rpm) / 100)*3)) #int((int(const_rpm) / 100) * ((int(hot_gpu) - int(temp_gpu_freeze))*2.5)) 
                stab_balance_mem =  int((int(mem_t) - int(target_mem_temp)) * ((int(const_rpm) / 100)*2)) #int((int(const_rpm) / 100) * ((int(mem_t) - (int(target_mem_temp)-2))*1.5))
                if stab_balance_mem < 0:
                    stab_balance_mem = 0
                if stab_balance <0:
                    stab_balance = 0
                print("оптимум - коректирую")
                print("stab_balance | stab_balance_mem" + str(stab_balance) + " " + str(stab_balance_mem))
                echo = int(optimun_echo) + int(stab_balance) + int(stab_balance_mem)
                if int(echo) < int(real_min_fan_rpm):
                    echo = int(real_min_fan_rpm)
                subprocess.getstatusoutput("echo " + str(echo) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan)) 
                print("echo", str(echo))
                get_temp()
                time.sleep(29)
                if int(hot_gpu) > (int(temp_gpu_freeze) + 3)  or int(hot_gpu) < (temp_gpu_freeze-2) or int(mem_t) >= (int(target_mem_temp) + 4) or (int(mem_t) < int(target_mem_temp)-4 and int(mem_t) != 0):            
                    print('::::::::::::::::::сбросил optimum_on::::::::::::::::::')
                    optimum_on = 0        
                    stable_temp_round = 0      
                    optimum_fan = 0     
                    boost_in_s = 0                                                                                                 
                    return()
                time.sleep(29)
    else:
        get_temp()
        subprocess.getstatusoutput("echo " + str(real_min_fan_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        time.sleep(29)
    return()

def addFanData(rpmfun, temp_gpu0,temp_gpu1,temp_gpu2,temp_gpu3,temp_gpu4,temp_gpu5,temp_gpu6,temp_gpu7,rpm_fun_gpu, alertFan,problemNumberGpu, hot_gpu):
    data={"id_in_serv": id_rig_in_server,'rpmfun':rpmfun,
                            'temp_gpu0':temp_gpu0, 'temp_gpu1':temp_gpu1,
                            'temp_gpu2':temp_gpu2,'temp_gpu3':temp_gpu3,
                            'temp_gpu4':temp_gpu4,'temp_gpu5':temp_gpu5,
                            'temp_gpu6':temp_gpu6,'temp_gpu7':temp_gpu7,
                            'rpm_fun_gpu':rpm_fun_gpu,
                            'alertFan':alertFan, 'problemNumberGpu':problemNumberGpu,
                            'hot_gpu':hot_gpu, 'hot_mem':mem_t
                            }
    try:
        r = requests.post("http://d132-188-243-182-20.ngrok.io/add_and_read_fandata/", data=data,stream=True, timeout=10)
    except Exception:
        print('ошибка в отправке данных по кулерам')
        time.sleep(60)
        try:
            r = requests.post("http://d132-188-243-182-20.ngrok.io/add_and_read_fandata/", data=data,stream=True, timeout=10)
        except Exception:
            time.sleep(10)
            try:
                send_mess('Failed to connect to the server, try to restart the rig | ', id_rig_in_server)
            except Exception:
                subprocess.run('reboot',shell=True)    
            subprocess.run('reboot',shell=True)

def get_temp():
    global rpmfun, hot_gpu, mem_t
    temp_gpu = []
    rpm_fun_gpu = {}
    alertFan = False
    problemNumberGpu = None
    numGpu=0
    try:
        mem_t = int(mem_temp())
    except Exception:
        mem_t = 0

    labels = ''
    for chip in sensors.iter_detected_chips():
        numGpu = numGpu+1                                                                                  
        if 'amdgpu' in str(chip) and str(chip) not in labels: 
            labels += ' ' + str(chip)                                                                                
            for feature in chip:
                if feature.label:
                    if str(feature.label) == "edge":  
                        try:                      
                            if int(feature.get_value()) == 511:
                                error511()                                                                        
                            temp_gpu.append(round(int(feature.get_value())))                                                                         
                        except Exception:
                            temp_gpu.append(0)
                        if str(feature.label) == '511':
                            error511()

    #добавляем данные кулеров с карт AMD если они есть
    labels = ''
    for chip in sensors.iter_detected_chips():                         
        if 'amd' in str(chip) and str(chip) not in labels:
            labels += ' ' + str(chip)
            for feature in chip:
                if str(feature.label) == "fan1": 
                    numGpu= str(chip).replace('amdgpu-', '')
                    try:
                        rpm_fun_gpu[str(numGpu)] = round(feature.get_value())
                    except Exception:
                        pass
    
    #добавляем данные температуры с карт nvidia если они есть
    (status,output)=subprocess.getstatusoutput("nvidia-smi -q | grep 'GPU Current Temp'")
    green_gpu_temp = output.replace('GPU Current Temp', '').replace(':', '').replace(' ', '').replace('C', ',').replace('\n38', ',').split(',')
    #print('green_gpu_temp', green_gpu_temp)
    for i in green_gpu_temp:
        if len(str(i)) != 0:
            temp_gpu.append(int(i))
            if str(i) == '511':
                error511()

    #добавляем данные кулеров с карт nvidia если они есть
    (status,output_fan)=subprocess.getstatusoutput("nvidia-smi -q | grep 'Bus Id\|Fan'")
    green_fan = output_fan.replace('Fan Speed', '').replace(' ', '').replace(':', '').replace('%', ',').replace('\n', ',').split(',')
    pci = ''
    fan_speed = ''
    for fan in green_fan:
        if len(str(fan)) != 0:
            if  "Bus" in str(fan):
                pci = 'pci-'+ str(fan.replace('BusId00000000', ''))
            else:
                fan_speed = fan
                rpm_fun_gpu[str(pci)] = round(int(3600 / 100 * int(fan_speed)))

    hot_gpu = max(temp_gpu)
    try:
        if statusAlertSystem == True and gpuFanSetHive == 1 and typeGpu == 0:
            #проверка кулеров на картах
            if round(rpm_fun_gpu[max(rpm_fun_gpu, key=rpm_fun_gpu.get)] - rpm_fun_gpu[max(rpm_fun_gpu, key=rpm_fun_gpu.get)]/10) > round(rpm_fun_gpu[min(rpm_fun_gpu, key=rpm_fun_gpu.get)]):
                #print("обнаружена проблема с кулерами")
                alertFan = True
                problemNumberGpu = min(rpm_fun_gpu, key=rpm_fun_gpu.get)
                #print(problemNumberGpu)
            else:
                alertFan = False
                problemNumberGpu = None
        else:
            alertFan = False
    except Exception as e:
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

    for chip in sensors.iter_detected_chips():
        if str(chip) == "nct6779-isa-0a30" :
            for feature in chip:                                                                                                      
                if str(feature.label) == "fan2":                                                         
                    # скорость внешних кулеров
                    if len(str(int(feature.get_value()))) !=0 or len(str(int(feature.get_value()))) != None:
                        rpmfun = int(feature.get_value())
                    else:
                       rpmfun = 0

    addFanData(rpmfun,temp_gpu0,temp_gpu1,temp_gpu2,temp_gpu3,temp_gpu4,temp_gpu5,temp_gpu6,temp_gpu7, rpm_fun_gpu, alertFan,problemNumberGpu,hot_gpu)
    return(True)

def testing():
    # начинаю тест железа
    global rpmfun
    def get_fan_rpm():
        temp_gpu = []
        rpm_fun_gpu = []
        for chip in sensors.iter_detected_chips():
            if str(chip) == "nct6779-isa-0a30" :
                for feature in chip:                                                                                                      
                    if str(feature.label) == "fan2":                                                                                      
                        #print("скорость внешних кулеров  ",feature.get_value())
                        rpmfun = feature.get_value()
                        return(int(rpmfun))
    if rpmfun != 0:
        pass
        #print("внешние кулера управляемые и крутятся")
    else:
        subprocess.getstatusoutput("echo 1 >>/sys/class/hwmon/hwmon1/pwm2_enable")
        subprocess.getstatusoutput("echo 80 >> /sys/class/hwmon/hwmon1/pwm2")
        #print("Внешних кулеров нет или они не управляемые")
        time.sleep(5)
        get_fan_rpm()
        if rpmfun != 0:
            print("Внешних кулеров нет или они не управляемые")
        return("There are no external coolers or they are not controlled, check the connections of the coolers to the motherboard. Make sure you are using WIND TANK TECHNOLOGIES L.L.C box")
    try:
        get_temp()
    except Exception:
        return("Data about video cards cannot be read, GPU may not be installed")

    print("тест завершился успешно")
    return(True)

def test_key(rig_id='', rig_name=''):                                                                                                 
    print("Зашли в test_key", len(str(rig_id)))                                                                                       
    global key_slave
                                                                                                          
    r_id = ""                                                                                                                         
    r_name = ""      
    try:                                                                                                                 
        for filename in glob.iglob('/hive-config/*.key_slave', recursive=True):                                                           
            file_key = open(filename, "r")
            key_slave = file_key.read()                                                                                                   
    except Exception:
        print("Ошибка ключа")
        test_key()                                                                                                     
    
    try:
        file1 = open("/hive-config/rig.conf", "r")                                                                                        
        lines = file1.readlines()  
        for line in lines:                                                                                                                
            if "WORKER_NAME=" in line:                                                                                                    
                r_name = line.replace("WORKER_NAME=", "").replace('"', '').replace('\n', '')                                              
                #print(r_name)                                                                                                             
        for line in lines:                                                                                                                
            if "RIG_ID" in line.split('='):
                r_id = line.replace("RIG_ID=", "").replace('\n', '')                                                                      
                #print(r_id)
                if  len(r_id) <2:
                    print("не нашел ID, Пробую еще")
                    engine_start()
                else:
                    if str(r_id) != str(rig_id) or rig_name != r_name:
                        print("***Изменился RIG ID или RIG NAME****")
                        with open('settings.json', 'r+') as f:
                            json_data = json.load(f)                                                                                                  
                            json_data['rig_id'] = str(r_id)                                                                                           
                            json_data['rig_name'] = str(r_name)                                                                                       
                            f.seek(0)                                                                                                                 
                            f.write(json.dumps(json_data))                                                                                            
                            f.truncate() 
                        subprocess.run('reboot',shell=True)


    except Exception:
        print("Ошибка открытия hive-config")
        test_key()
    
    if len(r_id)<2 or len(r_name)< 2:
        print('ОШИБКА имя или id слишком короткие, пробую еще раз')
        engine_start()
    else:
        if len(str(rig_id)) == 0:                                                                                                         
            print("Это первый запуск, прописываю ID в память")                                                                            
            with open('settings.json', 'r+') as f:
                json_data = json.load(f)                                                                                                  
                json_data['rig_id'] = str(r_id)                                                                                           
                json_data['rig_name'] = str(r_name)                                                                                       
                f.seek(0)                                                                                                                 
                f.write(json.dumps(json_data))                                                                                            
                f.truncate()  
            subprocess.run('reboot',shell=True)


    if str(rig_id) == str(r_id) and len(rig_id) >=1 and len(rig_name) >=1 and str(r_name) == str(rig_name):
        return(True)
    else:
        engine_start()



def send_mess_of_change_option(id_rig_in_server):
    try:
        send_mess(' Settings changed', id_rig_in_server)
    except Exception as e:
        send_mess(' Error - please pass this message on to the developer ' + str(e), id_rig_in_server)
    return(True)

def search_min_fan_rpm_now(static_option = None):
    global min_fan_rpm                                                                                                                                                                                 
    global real_min_fan_rpm  
    global stable_temp_round
    set_ok=0
    print("::::::::  ищу min fan или статик мод min fan   :::::::::::")                                      
    if static_option == None:
        mr = (int(rigRpmFanMaximum) / 100) * int(min_fan_rpm_persent)
        mr_min = mr - 100
        mr_max = mr + 100
        mr_min1 = mr - 200
        mr_max1 = mr + 200
    else:
        mr = (int(rigRpmFanMaximum) / 100) * int(static_option)
        mr_min = mr - 100
        mr_max = mr + 100
        mr_min1 = mr - 200
        mr_max1 = mr + 200
    step = 0
    with open('coolers.json', "r+") as file:
        data = json.load(file)
        for i in data:
            step = step+1
            for k, v in i.items():
                if int(mr_max1) < int(v) and step == 1:
                    real_min_fan_rpm =  int(k) 
                    set_ok = 1 
                    if static_option == None:
                        send_mess(' The desired speed of '+ str(int(mr))+ ' cannot be set because the minimum speed for these coolers is ' + str(v) + ' rpm', id_rig_in_server) 
                    else:
                        os.system("echo " + str(int(k)) +" >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
                        send_mess(' The desired speed of '+ str(int(mr))+ ' cannot be set because the minimum speed for these coolers is ' + str(v) + ' rpm', id_rig_in_server) 
                else:
                    if int(v) >= int(mr_min) and int(v) <= int(mr_max):
                        real_min_fan_rpm =  int(k) 
                        set_ok = 1 
                        if static_option == None:
                            send_mess(' Minimum speed set ' + str(v) + ' rpm', id_rig_in_server) 
                            break
                        else:
                            os.system("echo " + str(int(k)) +" >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
                            send_mess(' Static speed set ' + str(v) + ' rpm', id_rig_in_server) 
                            break
        if set_ok == 1:
            pass
        else:
            for i in data:
                for k, v in i.items():
                    if int(v) >= int(mr_min1) and int(v) <= int(mr_max1):
                        real_min_fan_rpm =  int(k) 
                        set_ok = 1 
                        if static_option == None:
                            send_mess(' Minimum speed set ' + str(int(v)) + ' rpm', id_rig_in_server) 
                        else:
                            os.system("echo " + str(int(k)) +" >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
                            send_mess(' Static speed set ' + str(v) + ' rpm', id_rig_in_server)            

        if set_ok == 1:
            pass
        else:
            send_mess(' Unfortunately, external coolers cannot work at a given speed due to their characteristics or incorrect calibration.Try to set the speed more!' + str(int(v)) + ' rpm', id_rig_in_server)

    stable_temp_round = 0
    get_temp()
    return(True)

def get_setting_server(id_rig_in_server,key_slave):
    try:
        response = requests.get('http://d132-188-243-182-20.ngrok.io/get_option_rig/', data = [('id_in_serv', id_rig_in_server),('key_slave',key_slave)],stream=True, timeout=10 )
    except Exception:
        time.sleep(90)
        engine_start()
    response = response.json()
    global selected_mod, gpu_status, terget_temp_min, terget_temp_max, min_fan_rpm, select_fan, boost, critical_temp, option1, statusAlertSystem, gpuFanSetHive,typeGpu,const_rpm, rigOnBoot, rigRpmFanMaximum, min_fan_rpm_persent, mod_option_hive, option2, target_mem_temp

    
    if const_rpm == 0:
        mod_option_hive = int(response["data"][0]["attributes"]["mod_option_hive"])
        rigRpmFanMaximum = int(response["data"][0]["attributes"]["rigRpmFanMaximum"])
        const_rpm = int(response["data"][0]["attributes"]["effective_echo_fan"])
        typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])
        gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])
        statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]
        selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
        terget_temp_min = int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_min"])
        terget_temp_max = int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_max"])
        min_fan_rpm_persent = response["data"][0]["attributes"]["SetMode0"]["min_fan_rpm"]
        select_fan = int(response["data"][0]["attributes"]["SetModeFan"]["select_fan"])
        critical_temp = int(response["data"][0]["attributes"]["SetMode0"]["critical_temp"])
        boost=int(response["data"][0]["attributes"]["SetMode0"]["boost"])
        option2 = response["data"][0]["attributes"]["SetMode2"]["SetRpm"]
        target_mem_temp = int(response["data"][0]["attributes"]["SetMode0"]["target_mem"])
        min_fan_rpm = int(const_rpm / 100 * int(response["data"][0]["attributes"]["SetMode0"]["min_fan_rpm"]))
        rigOnBoot = 1
        gpu_status = response["data"][0]["attributes"]["gpu_status"]
    else:
        if gpu_status != response["data"][0]["attributes"]["gpu_status"]:
            gpu_status = response["data"][0]["attributes"]["gpu_status"]
        if const_rpm != int(response["data"][0]["attributes"]["effective_echo_fan"]):
            const_rpm = int(response["data"][0]["attributes"]["effective_echo_fan"])

        if typeGpu != int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"]):
            typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])

        if gpuFanSetHive != int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"]):
            gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])

        if statusAlertSystem != response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]:
            statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]

        if selected_mod != int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"]):
            selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])

        if terget_temp_min != int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_min"]):
            terget_temp_min = int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_min"])

        if terget_temp_max != int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_max"]):
            terget_temp_max = int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_max"])

        if min_fan_rpm !=  int(const_rpm / 100 * int(response["data"][0]["attributes"]["SetMode0"]["min_fan_rpm"])):
            min_fan_rpm = int(const_rpm / 100 * int(response["data"][0]["attributes"]["SetMode0"]["min_fan_rpm"]))

        if select_fan != int(response["data"][0]["attributes"]["SetModeFan"]["select_fan"]):
            select_fan = int(response["data"][0]["attributes"]["SetModeFan"]["select_fan"])


        if critical_temp != int(response["data"][0]["attributes"]["SetMode0"]["critical_temp"]):
            critical_temp = int(response["data"][0]["attributes"]["SetMode0"]["critical_temp"])


        if boost != int(response["data"][0]["attributes"]["SetMode0"]["boost"]):
            boost=int(response["data"][0]["attributes"]["SetMode0"]["boost"])


        if option2 != response["data"][0]["attributes"]["SetMode2"]["SetRpm"]:
            option2 = response["data"][0]["attributes"]["SetMode2"]["SetRpm"]


        if target_mem_temp !=  int(response["data"][0]["attributes"]["SetMode0"]["target_mem"]):
            target_mem_temp =  int(response["data"][0]["attributes"]["SetMode0"]["target_mem"])
            
        if mod_option_hive != int(response["data"][0]["attributes"]["mod_option_hive"]):
            mod_option_hive = int(response["data"][0]["attributes"]["mod_option_hive"])

        if min_fan_rpm_persent != response["data"][0]["attributes"]["SetMode0"]["min_fan_rpm"]:
            min_fan_rpm_persent = int(response["data"][0]["attributes"]["SetMode0"]["min_fan_rpm"])

    # проверяем включена ли реколебровка и если нужно запускаем
    if response["data"][0]["attributes"]["recalibrationFanRig"] == True:
        testFan(id_rig_in_server)
        get_setting_server(id_rig_in_server, key_slave)
    return("true")

def get_setting_server1(id_rig_in_server, key_slave):
    try:
        response = requests.get('http://d132-188-243-182-20.ngrok.io/get_option_rig/', data = [('id_in_serv', id_rig_in_server),('key_slave',key_slave)] ,stream=True, timeout=10)
    except Exception:
        time.sleep(90)
        engine_start()
    response = response.json()
    global option1, selected_mod, statusAlertSystem, gpuFanSetHive, typeGpu, rigOnBoot, const_rpm
    cache = 0
    if cache == 0:
        rigRpmFanMaximum = int(response["data"][0]["attributes"]["rigRpmFanMaximum"])
        const_rpm = int(response["data"][0]["attributes"]["effective_echo_fan"])
        typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])
        gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])
        statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]
        selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
        cache = response["data"][0]["attributes"]["SetMode1"]
        rigOnBoot =1
    else:
        if typeGpu != int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"]):
            typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])


        if gpuFanSetHive != int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"]):
            gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])

        if statusAlertSystem != response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]:
            statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]

        if selected_mod != int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"]):
            selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])

        if cache != response["data"][0]["attributes"]["SetMode1"]:
            cache = response["data"][0]["attributes"]["SetMode1"]
    del cache['id']
    for i in cache:
        key1 = i.replace('t', '')
        vals = cache[i].split(",")
        two_val = []
        for val in vals:
            two_val.append(int(val))
        #print(key1, two_val)
        option1.update({str(key1):two_val}) 
    return("true")
    
def get_setting_server2(id_rig_in_server, key_slave):
    try:
        response = requests.get('http://d132-188-243-182-20.ngrok.io/get_option_rig/', data = [('id_in_serv', id_rig_in_server),('key_slave',key_slave)],stream=True, timeout=10 )
    except Exception:
        time.sleep(90)
        engine_start()
    response = response.json()
    global option2, selected_mod, statusAlertSystem, gpuFanSetHive, typeGpum, rigOnBoot, mod_option_hive

    if rigOnBoot ==0:
        mod_option_hive = int(response["data"][0]["attributes"]["mod_option_hive"])
        rigRpmFanMaximum = int(response["data"][0]["attributes"]["rigRpmFanMaximum"])
        typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])
        gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])
        statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]
        selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
        option2 = response["data"][0]["attributes"]["SetMode2"]["SetRpm"]
        rigOnBoot =1
    else:
        if typeGpu != int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"]):
            typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])


        if gpuFanSetHive != int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"]):
            gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])

        if statusAlertSystem != response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]:
            statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]
 
        if selected_mod != int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"]):
            selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])

        if option2 != response["data"][0]["attributes"]["SetMode2"]["SetRpm"]:
            option2 = response["data"][0]["attributes"]["SetMode2"]["SetRpm"]

        if mod_option_hive != int(response["data"][0]["attributes"]["mod_option_hive"]):
            mod_option_hive = int(response["data"][0]["attributes"]["mod_option_hive"])
    return("true")

def checking_new_settings(id, applyOptionReady = None):
    try:
        param= [('rigId', id), ('applyOptionReady',applyOptionReady)]
        response = requests.post('http://d132-188-243-182-20.ngrok.io/get_status_new_option/', data = param ,stream=True, timeout=10)
        print("Статус настроек", response.json()["data"])
        if int(response.json()["data"]) == 1:
            engine_start()
        else:
            pass
    except Exception as e:
        print("Ошибка получения статуса настроек",e)


def sendInfoRig(rig_id, rig_name, key_slave, device_name):
    global id_rig_in_server
    param= [('rigId', rig_id), ('rigName', rig_name), ('key_slave',key_slave), ('device_name', device_name)] 
    try:
        response = requests.post('http://d132-188-243-182-20.ngrok.io/add_rig_or_test/', data = param ,stream=True, timeout=10)
        print('sendInfoRig ',response)
    except Exception as e:
        print('Ошибка sendInfoRig',e)
        time.sleep(90)
        engine_start()
    id_rig_in_server = response.json()["data"]
    checking_new_settings(id_rig_in_server, applyOptionReady = 0)
    return(True)

def server_pci_status_list(str):                              
    print("Пришлов обработку", str)
    lists = []                                                     
    try:                                                             
        for i in str.split(','):
            lists.append({i.split("'",2)[1].replace('{','').replace('}','').replace("'",'').replace(']','').replace('[',''):i.split(':')[2].replace("}",'').replace('"','').replace("'",'').replace(']','').replace(' ','').replace('[','').replace("'",'')})
    except Exception:
        pass                                                                                                                                                    
    return (lists)                                                      
def touch_pci_status_file(id, w):
    #print("Буду записывать в json",w)
    with open('pci_status_file.json', "w+") as file:
        file.seek(0)
        file.write(json.dumps(w))
        file.truncate()
    if id != None:
        param= [('rigId', id), ('work_pci', str(w))]
        response = requests.post('http://d132-188-243-182-20.ngrok.io/rig_pci_status/', data = param ,stream=True, timeout=10)
    applay_pci_status(w)         

def re_pci_status():
    server_pci_status_file = server_pci_status_list(gpu_status)               
    id = id_rig_in_server                                                                                                             
    work_pci = []                                                    
    (status,output_fan)=subprocess.getstatusoutput("sudo lspci -v | grep --color -E '(VGA|3D)'")
    all_pci = re.split('\n', output_fan)
    for i in all_pci:
        if "VGA controller" not in str(i.split('[', 1)[1].split(']')[0]):  
            name = str(i.split('[', 1)[1].split(']')[0]).replace('RTX','').replace('NVIDIA','').replace('AMD','').replace('GeForce','').replace('NVIDIA','').replace('/Max-Q','').replace(' ','').replace("''",'')           
            if name == '/ATI':
                name = 'AMD ' + str(i.split('[')[2].split(']')[0].replace('Radeon','').replace('RX','').replace(' ','')[0:3].replace('/',''))
            work_pci.append({str(i.split(' ')[0])+' ('+str(name)+')': True})
    if test(server_pci_status_file) != False:
        print("Карты стоят теже самые")
        touch_pci_status_file(id, server_pci_status_file)
    else:
        touch_pci_status_file(id, work_pci)
        
        
    #obj1 = {}                                                       
    #obj2 = {}     
    #with open('/home/fanonrig/init_gpu.json', 'r') as f:
    #    f_init_gpu = json.load(f)      
    #                                                
    #for i in range(0, len(f_init_gpu)):
    #    for key,value in work_pci[i].items():
    #        obj1[key] = value                                                  
    #for i in range(0, len(server_pci_status_file)):
    #    for key,value in server_pci_status_file[i].items():
    #        obj2[key] = value
    #
    #for i in obj2:
    #    try:                                          
    #        obj1[i]
    #    except Exception as e:
    #        print("Карты в слотах не совпадают, записываем новый порядок", e) 
    #        touch_pci_status_file(id, work_pci)
    #        return()
    #if len(work_pci) > len(server_pci_status_file):
    #    print("Карт стало больше, записываем новый порядок")
    #    touch_pci_status_file(id, work_pci)
    #else:                                                              
    #    print("Карты прежнии")
    #    work_pci = server_pci_status_file                                                    
    #    touch_pci_status_file(id, server_pci_status_file) 

def test_select_mod(): # Проверяем режим работы
    try:
        if selected_mod == old_selected_mod:
            pass
        else:
            engine_start()
    except Exception:
        print("Не удалось проверить режим работы, возможно сервер не ответил")
        

def engine_start():
    global last_rpm, boost_in_s, stable_temp_round, optimum_fan, optimum_temp, optimum_on, optimun_echo, start_optimum, temp_gpu_freeze, old_stab_balance, optimum_round, last_rpm_s, old_selected_mod, selected_mod, terget_temp_min, terget_temp_max, min_fan_rpm, hot_gpu, critical_temp, const_rpm, select_fan, rpmfun, option1, option2, id_rig_in_server, ressetRig, soft_rev, device_name
    #скидываем в 0 если там были данные
    last_rpm_s = 0
    last_rpm = 0
    boost_in_s = 0
    stable_temp_round = 0
    optimum_fan = 0
    optimum_on = 0
    optimun_echo = 0
    start_optimum = 0
    temp_gpu_freeze = 0
    old_stab_balance = 0
    optimum_round = 0
    old_min_fan = 0
    old_option2 = 0
    #снижаем шум до загрузки мода
    subprocess.getstatusoutput("echo 1 >>/sys/class/hwmon/hwmon1/pwm2_enable")
    subprocess.getstatusoutput("echo 15 >> /sys/class/hwmon/hwmon1/pwm2") 
    testing()  # проверяем работоспособность самого рига
    with open('settings.json', 'r', encoding='utf-8') as f: #открыли файл с данными
        text = json.load(f)
    rig_id = str(text["rig_id"])
    rig_name = str(text["rig_name"])
    soft_rev = str(text["soft_rev"])
    try:
        device_name = str(text["device_name"])
    except Exception:
        device_name = 'Wind Tank V1'
    old_selected_mod = selected_mod # проверяем какой мод установлен
    test_key(rig_id, rig_name) # проверям имя рига, ключ, и т.д
    # передаем данные о риге и получаем ответ с id
    try:
        sendInfoRig(rig_id,rig_name, key_slave, device_name)
    except Exception as e:
        print(e)
    
    if ressetRig == True:
        try:
            requests.post("http://d132-188-243-182-20.ngrok.io/ressetRigAndFanData/", data={'ressetRig':'True', 'id_rig_in_server':id_rig_in_server},stream=True, timeout=10)
        except Exception as e:
            time.sleep(90)
            print('ошибка ressetRig ',e)
            engine_start()
        ressetRig = False

    try:
        get_temp()
    except Exception:
        print("Проблема с получением данных, возможно в риге нет карт")
        engine_start()
    try:
        get_setting_server(id_rig_in_server, key_slave)
        if selected_mod == 1:
            pass
        elif selected_mod == 1:
            get_setting_server1(id_rig_in_server, key_slave)
        elif selected_mod == 2:
            get_setting_server2(id_rig_in_server, key_slave)
        print("ответ с сервера получен")
    except Exception:
        print("нет ответа с сервера, перезапускаю engine")
        time.sleep(90)
        engine_start()

    try:
        task_update(id_rig_in_server, str(soft_rev))
    except Exception:
        time.sleep(90)
        print("ошибка запроса на обновление")
        engine_start()
    re_pci_status()     # Отключаем или включаем PCI
    if selected_mod == 0:
        if int(min_fan_rpm_persent) == None:  # если это первый страрт с реколибровкой, то будет NONE
            os.system("reboot")
            subprocess.run('reboot',shell=True)

        send_mess(' Intelligent mode activated', id_rig_in_server)
        subprocess.getstatusoutput("echo 1 >>/sys/class/hwmon/hwmon1/pwm"+str(select_fan)+"_enable")
        subprocess.getstatusoutput("echo " + str(round(const_rpm / 100 * int(option2))) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))       
        while 1 > 0:
            checking_new_settings(id_rig_in_server)
            if int(min_fan_rpm) != int(old_min_fan):
                old_min_fan = int(min_fan_rpm)
                try:
                    search_min_fan_rpm_now()
                except Exception as e:
                    print("проблема в search_min_fan_rpm_now",e) 
            active_cool_mod()
            try:
                test_select_mod()
                try:
                    if mod_option_hive == 1:
                        communication_hive(id_rig_in_server, key_slave, mod_option_hive, const_rpm, rpmfun,rigRpmFanMaximum, option2, terget_temp_min,terget_temp_max, min_fan_rpm_persent, target_mem_temp, selected_mod,device_name)
                        print("*** Активно управление из HIVE ***")
                    else:
                        pass
                except Exception as e:
                    print('erroe in hive mode',e)
            except Exception as e:
                print("ERROR selected_mod0 " + str(e))
                engine_start()
                
    elif selected_mod == 1:
        print("Выбран ручной режим")
        subprocess.getstatusoutput("echo 1 >>/sys/class/hwmon/hwmon1/pwm"+str(select_fan)+"_enable")
        send_mess(' Manual mode activated', id_rig_in_server)
        while 1 > 0:
            checking_new_settings(id_rig_in_server)
            test_select_mod()
            time.sleep(50)
            get_temp()
            for i in option1:
                if hot_gpu >= option1[i][0] and  hot_gpu <= option1[i][1]:
                    last_rpm = int(int(const_rpm / 100) * int(i))
                    subprocess.getstatusoutput("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
                    #print("выдаю  ",i,"%",  "горячая карта ", hot_gpu)
    elif selected_mod == 2:
        #print("Выбран статичный режим")
        subprocess.getstatusoutput("echo 1 >>/sys/class/hwmon/hwmon1/pwm"+str(select_fan)+"_enable")
        send_mess(' Static mode activated', id_rig_in_server)
        while 1 > 0:
            checking_new_settings(id_rig_in_server)
            time.sleep(50)
            try:
                if mod_option_hive == 1:
                    communication_hive(id_rig_in_server, key_slave, mod_option_hive, const_rpm, rpmfun,rigRpmFanMaximum, option2, terget_temp_min,terget_temp_max, min_fan_rpm_persent, target_mem_temp, selected_mod,device_name)
                    print("*** Акстивно управление из HIVE ***")
                else:
                    pass
            except Exception as e:
                print('erroe in hive mode',e)
            get_temp()
            test_select_mod()
            if int(option2) != int(old_option2):
                old_option2 = int(option2)
                try:
                    search_min_fan_rpm_now(int(option2))
                except Exception as e:
                    print("проблема в search_min_fan_rpm_now",e) 
            option = int(const_rpm / 100 * int(option2))
            subprocess.getstatusoutput("echo " + str(option) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
            print("echo " + str(option) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))

def apdate_fan_sh():
    subprocess.getstatusoutput("cp -u /home/onrig/fan.sh /home/")
    subprocess.getstatusoutput("sudo chmod ugo+x /home/onrig/fan.sh")
    subprocess.getstatusoutput("sudo rm /home/onrig/fan.sh")


if __name__ == '__main__':
    if os.path.exists("coolers.json") == True:
        pass
    else:
        subprocess.getstatusoutput("touch /run/hive/fan_controller_recallibrate_req")
    #if os.path.exists("/home/onrig/fan.sh") == True:
    #    apdate_fan_sh()
    #    time.sleep(5)
    #    #os.system("reboot")
    #    #subprocess.run('reboot',shell=True)
    #else:
    #    pass
    try:
        engine_start()
    except Exception as e:
        send_mess('ОError in ENGINE CORE - send a text message to the developer | ' + str(e), id_rig_in_server)
        #os.system("reboot")
        #subprocess.run('reboot',shell=True)
