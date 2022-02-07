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
import sensors
sensors.init()


old_selected_mod = 0
selected_mod = 0
terget_temp_min = 0
terget_temp_max = 0
min_fan_rpm = 30
hot_gpu = 0
critical_temp = 0
const_rpm = 255
last_rpm = 100
select_fan = 0
boost = 0
rigRpmFanMaximum = 5500
rigRpmFaneffective = 4100
rpmfun= 3500
option1 = {}
option2 = 100
id_rig_in_server = 0
statusAlertSystem = False
gpuFanSetHive = 0
typeGpu = 0
ressetRig=True

def active_cool_mod():
    global last_rpm
    global boost
    print("НОВЫЙ const_rpm",const_rpm)
    if hot_gpu >= terget_temp_min and hot_gpu < critical_temp:
        print('boost', (hot_gpu+1), '-', terget_temp_min, '*', boost, '+', int(min_fan_rpm))
        xfactor = ((hot_gpu+1) - terget_temp_min) * boost + int(min_fan_rpm)
        print("xfactor",xfactor)
        corect_boost = const_rpm / 100 * xfactor
        if last_rpm != corect_boost:
            last_rpm = int(corect_boost)
            os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
            print("удерживаю, даю", int(last_rpm))
        else:
            print("температура стабильна")
    if hot_gpu < terget_temp_min -2:
        last_rpm = int((const_rpm / 10) *1 )
        os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        print("температура ниже уровня, даю ",last_rpm)
    if hot_gpu == terget_temp_min - 2:
        last_rpm = int(const_rpm / 100 * 25)
        os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        print("температура ниже уровня но подходит к уровню удержания, даю ",last_rpm)
    if hot_gpu == terget_temp_min - 1:
        last_rpm = int(const_rpm / 100 * 3)
        os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        print("температура ниже уровня но подходит к уровню удержания, даю ",last_rpm)
        print(hot_gpu)

    if hot_gpu >= critical_temp:
        print("температура критическая, выполняю защитный алгоритм!")
        os.system("miner stop")
        time.sleep(7)
        os.system("miner stop")
        print("майнер остановлен")
    if hot_gpu >= critical_temp +5 :
        print("температура выше критической на 5 , выполняю защитный алгоритм!")
        os.system("sreboot shutdown")

def addFanData(rpmfun, temp_gpu0,temp_gpu1,temp_gpu2,temp_gpu3,temp_gpu4,temp_gpu5,temp_gpu6,temp_gpu7,rpm_fun_gpu, alertFan,problemNumberGpu, hot_gpu):
    print('ЗАШЛИ В ВЫДАЧУ ДАННЫХ О КУЛЕРАХ')
    time.sleep(20)
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
    rpm_fun_gpu = {'0':600,'1':1000,'2':1050,'3':1020,'4':1030,'5':1000,'6':1000,'7':1040}
    numGpu=0
    alertFan = False
    problemNumberGpu = None
    try:
        for chip in sensors.iter_detected_chips():                                                                                        
            if str(chip.adapter_name) == "PCI adapter":                                                                                   
                for feature in chip:                                                                                                      
                    try:             
                        numGpu = numGpu+1                                                                                                     
                        if str(feature.label) == "edge":                                                                                  
                            #print(feature.get_value())     # температура
                            temp_gpu.append(round(feature.get_value()))
                        if str(feature.label) == "fan1": 
                            #print(feature.get_value())    # скорость кулеров
                            #rpm_fun_gpu.append({str(numGpu):feature.get_value()})
                            rpm_fun_gpu[str(numGpu)] = feature.get_value()
                    except Exception:
                        pass
        #добавляем данные с карт nvidia если они есть
        (status,output)=subprocess.getstatusoutput("nvidia-smi -q | grep 'GPU Current Temp'")
        green_gpu_temp = output.replace('GPU Current Temp', '').replace(':', '').replace(' ', '').replace('C', ',').replace('\n38', ',').split(',')
        print('green_gpu_temp', green_gpu_temp)
        for i in green_gpu_temp:
            if len(i) != 0:
                temp_gpu.append(int(i))
        print("Найдено карт", len(temp_gpu)) #вывели результат на экран
        print(temp_gpu)
        hot_gpu = max(temp_gpu)
        print("Самая горячая карта", max(temp_gpu)) #вывели результат на экран
        print("самая высокая скорость кулера видеокарты!", rpm_fun_gpu[max(rpm_fun_gpu, key=rpm_fun_gpu.get)]) #вывели результат на экран
        print("!!!",statusAlertSystem == True, gpuFanSetHive == 1, typeGpu == 0)
        try:
            if statusAlertSystem == True and gpuFanSetHive == 1 and typeGpu == 0:
                print("зашли в проверку кулеров",rpm_fun_gpu[max(rpm_fun_gpu, key=rpm_fun_gpu.get)] - rpm_fun_gpu[max(rpm_fun_gpu, key=rpm_fun_gpu.get)]/10, rpm_fun_gpu[min(rpm_fun_gpu, key=rpm_fun_gpu.get)])
                if rpm_fun_gpu[max(rpm_fun_gpu, key=rpm_fun_gpu.get)] - rpm_fun_gpu[max(rpm_fun_gpu, key=rpm_fun_gpu.get)]/10 > rpm_fun_gpu[min(rpm_fun_gpu, key=rpm_fun_gpu.get)]:
                    print("обнаружена проблема с кулерами")
                    alertFan = True
                    problemNumberGpu = min(rpm_fun_gpu, key=rpm_fun_gpu.get)
                else:
                    alertFan = False
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
        #temp_gpu1 = temp_gpu[1]
        #temp_gpu2 = temp_gpu[2]
        #temp_gpu3 = temp_gpu[3]
        #temp_gpu4 = temp_gpu[4]
        #temp_gpu5 = temp_gpu[5]
        #temp_gpu6 = temp_gpu[6]
        #temp_gpu7 = temp_gpu[7]
        addFanData(rpmfun,temp_gpu0,temp_gpu1,temp_gpu2,temp_gpu3,temp_gpu4,temp_gpu5,temp_gpu6,temp_gpu7, rpm_fun_gpu, alertFan,problemNumberGpu,hot_gpu)
    except Exception:
        pass
        time.sleep(3)

    for chip in sensors.iter_detected_chips():
        if str(chip) == "nct6779-isa-0a30" :
            for feature in chip:                                                                                                      
                if str(feature.label) == "fan2":                                                                                      
                    print("скорость внешних кулеров  ",feature.get_value())
                    rpmfun = feature.get_value()

def testing():
    print("начинаю тест железа")
    global rpmfun
    temp_gpu = []
    rpm_fun_gpu = []
    for chip in sensors.iter_detected_chips():
        if str(chip) == "nct6779-isa-0a30" :
            for feature in chip:                                                                                                      
                if str(feature.label) == "fan2":                                                                                      
                    print("скорость внешних кулеров  ",feature.get_value())
                    rpmfun = feature.get_value()
    if rpmfun != 0:
        print("внешние кулера управляемые и крутятся")
    else:
        print("внешних кулеров нет или они не управляемые")
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
    	print("обнаружено ",len(temp_gpu), "карт" )
    	print(temp_gpu)
    	print(rpm_fun_gpu)
    else:
    	print("видеокарт не обнаружено, сорян")
    	sys.exit()
    print("тест завершился успешно")
    time.sleep(3)

def test_key(rig_id, rig_name):
    r_id = "" 
    r_name = ""
    file1 = open("/hive-config/rig.conf", "r")
    lines = file1.readlines()
    for line in lines:
        if "WORKER_NAME=" in line:
            r_name = line.replace("WORKER_NAME=", "").replace('"', '')
        if "RIG_ID" in line:
            r_id = line.replace("RIG_ID=", "")
            print("RIG_ID",line.replace("RIG_ID=", ""))
            if len(rig_id) == 0:
                print("Это первый запуск, прописываю ID в память")
                with open('settings.json', 'r+') as f:
                    json_data = json.load(f)
                    json_data['rig_id'] = str(r_id)
                    json_data['rig_name'] = str(r_name)
                    f.seek(0)
                    f.write(json.dumps(json_data))
                    f.truncate()

            if str(rig_id) == str(line.replace("RIG_ID=", "")):
                print("Защита пройдена и в этот раз я не сотру систему")
            if len(rig_id) != 0 and rig_id != r_id:
                print("rig id не совпадает, стираю систему")
                sys.exit()
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
    const_rpm = int(response["data"][0]["attributes"]["effective_echo_fan"])
    typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])
    gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])
    statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]
    selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
    terget_temp_min = int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_min"])
    terget_temp_max = int(response["data"][0]["attributes"]["SetMode0"]["terget_temp_max"])
    min_fan_rpm = int(response["data"][0]["attributes"]["SetMode0"]["min_fan_rpm"])
    select_fan = int(response["data"][0]["attributes"]["SetModeFan"]["select_fan"])
    critical_temp = int(response["data"][0]["attributes"]["SetMode0"]["critical_temp"])
    boost=int(response["data"][0]["attributes"]["SetMode0"]["boost"])
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
	typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])
	gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])
	statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]
	selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
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
	typeGpu = int(response["data"][0]["attributes"]["AlertFan"]["typeGpu"])
	gpuFanSetHive = int(response["data"][0]["attributes"]["AlertFan"]["gpuFanSetHive"])
	statusAlertSystem = response["data"][0]["attributes"]["AlertFan"]["statusAlertSystem"]
	selected_mod = int(response["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
	option2 = response["data"][0]["attributes"]["SetMode2"]["SetRpm"]
	return("true")

def sendInfoRig(rig_id, rig_name):
    global id_rig_in_server
    try:
        param= [('rigId', rig_id), ('rigName', rig_name)] 
        response = requests.post('http://ggc.center:8000/add_rig_or_test/', data = param )
        id_rig_in_server = response.json()["data"]
        #print('id_rig_in_server тут смотреть',id_rig_in_server)
    except Exception as e:
        print('ошибка в sendInfoRig', e)
        time.sleep(10)
        sendInfoRig(rig_id, rig_name)
    time.sleep(30)
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

    #testing()

    with open('settings.json', 'r', encoding='utf-8') as f: #открыли файл с данными
        text = json.load(f) #загнали все, что получилось в переменную
    print("Конфиг загружен и валиден", text) #вывели результат на экран
    print("начинаю тест безопастности")
    rig_id = str(text["rig_id"])
    rig_name = str(text["rig_name"])
    old_selected_mod = selected_mod
    #test_key(rig_id, rig_name)
    # передаем данные о риге и получаем ответ с id
    sendInfoRig(rig_id,rig_name)
    if ressetRig == True:
        requests.post("http://ggc.center:8000/ressetRigAndFanData/", data={'ressetRig':'True', 'id_rig_in_server':id_rig_in_server})
        ressetRig = False
    else:
        pass
    # передача данных о риге завершена
    if get_setting_server(id_rig_in_server) == "true":
        print("ответ с сервера получен")
    else:
        print("нет ответа с сервера")
        selected_mod=int(text["selected_mod"])
        terget_temp_min = text['0']['terget_temp_min']
        terget_temp_max = text['0']['terget_temp_max']
        min_fan_rpm = text['0']['min_fan_rpm']
        select_fan = text['select_fan']
        critical_temp = text['0']['critical_temp']
        boost = text['0']['boost']
    if selected_mod == 0:
        print("Выбран режиж удержания температур в диапазоне" , terget_temp_min, terget_temp_max)
        print("начинаю вычесления, а пока что продуем систему")
        os.system("echo 1 >>/sys/class/hwmon/hwmon1/pwm"+str(select_fan)+"_enable")
        os.system("echo 100 >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        while 1 > 0:
            test_select_mod()
            time.sleep(7)
            get_setting_server(id_rig_in_server)
            get_temp()
            active_cool_mod()
    elif selected_mod == 1:
        print("Выбран ручной режим")
        os.system("echo 1 >>/sys/class/hwmon/hwmon1/pwm"+str(select_fan)+"_enable")
        os.system("echo 100 >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
        while 1 > 0:
            test_select_mod()
            time.sleep(7)
            get_temp()
            if get_setting_server1(id_rig_in_server) == "true":
                print("ответ с сервера получен")
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
        while 1 > 0:
            time.sleep(7)
            if get_setting_server2(id_rig_in_server) == "true":
                print("ответ с сервера получен")
                get_temp()
                test_select_mod()
            else:
                test_select_mod()
                get_temp()
                option2 = round(const_rpm / 100 * int(text["2"]))
            os.system("echo 1 >>/sys/class/hwmon/hwmon1/pwm"+str(select_fan)+"_enable")
            print("echo " + str(option2) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))



if __name__ == '__main__':
	try:
		engine_start()
	except Exception as e:
		print(e)
		engine_start()
	#get_temp()
