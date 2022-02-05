import json #подключили библиотеку для работы с json
from pprint import pprint #подключили Pprint для красоты выдачи текста
import os
import time
import sys
import sensors
sensors.init()

terget_temp_min = 0
terget_temp_max = 0
hot_gpu = 0
critical_temp = 0
const_rpm = 255
last_rpm = 100
select_fan = 0
boost = 0
rpmfun= 0
def active_cool_mod():
	global last_rpm
	global boost
	if hot_gpu >= terget_temp_min and hot_gpu < critical_temp:
		xfactor = (hot_gpu - terget_temp_min) * boost + 40
		print("xfactor",xfactor)
		corect_boost = const_rpm / 100 * xfactor
		if last_rpm != corect_boost:
			last_rpm = corect_boost
			os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
			print("удерживаю, даю",corect_boost)
		else:
			print("температура стабильна")
	if hot_gpu < terget_temp_min -2:
		last_rpm = (const_rpm / 10) *3 
		os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
		print("температура ниже уровня, даю ",last_rpm)
	if hot_gpu == terget_temp_min - 2:
		last_rpm = const_rpm / 100 * 35
		os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
		print("температура ниже уровня но подходит к уровню удержания, даю ",last_rpm)
	if hot_gpu == terget_temp_min - 1:
		last_rpm = const_rpm / 100 * 40
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


def get_temp():
	try:
		with open('t.json', 'r', encoding='utf-8') as t: #открыли файл с данными
			gpu_t = json.load(t) #загнали все, что получилось в переменную
		print("Найдено карт", len(gpu_t["t"])) #вывели результат на экран
		global hot_gpu
		hot_gpu = max(gpu_t["t"])
		print("Самая горячая карта", max(gpu_t["t"])) #вывели результат на экран

	except Exception as e:
		print(e)
		time.sleep(3)

def testing():
	print("начинаю тест железа")
	global rpmfun
	temp_gpu = []
	rpm_fun_gpu = []
	for chip in sensors.iter_detected_chips():                                                                                        
    	if str(chip) == "nct6779-isa-0a30":                                                                                           
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
	r_name ""
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
				

			if rig_id == line.replace("RIG_ID=", ""):
				print("Защита пройдена и в этот раз я не сотру систему")
			else:
				print("rig id не совпадает, стираю систему")
				sys.exit()
if __name__ == '__main__':
	testing()
	with open('settings.json', 'r', encoding='utf-8') as f: #открыли файл с данными
		text = json.load(f) #загнали все, что получилось в переменную
	print("Конфиг загружен и валиден", text) #вывели результат на экран
	print("начинаю тест безопастности")
	rig_id = str(text["rig_id"])
	rig_name = str(text["rig_name"])
	test_key(rig_id, rig_name)
	selected_mod=int(text["selected_mod"])
	terget_temp_min = text['0']['terget_temp_min']
	terget_temp_max = text['0']['terget_temp_max']
	select_fan = text['select_fan']
	critical_temp = text['0']['critical_temp']
	boost = text['0']['boost']
	if selected_mod == 0:
		print("Выбран режиж удержания температур в диапазоне" , terget_temp_min, terget_temp_max)
		print("начинаю вычесления, а пока что продуем систему")
		os.system("echo 1 >>/sys/class/hwmon/hwmon1/pwm"+str(select_fan)+"_enable")
		os.system("echo 255 >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
		while 1 > 0:
			time.sleep(7)
			get_temp()
			active_cool_mod()
	elif selected_mod == 1:
		print("Выбран ручной режим")
		os.system("echo 1 >>/sys/class/hwmon/hwmon1/pwm"+str(select_fan)+"_enable")
		os.system("echo 255 >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
		while 1 > 0:
			time.sleep(7)
			get_temp()
			for i in text["1"]:
				if hot_gpu >= text["1"][i][0] and  hot_gpu <= text["1"][i][1]:
					last_rpm = const_rpm / 100 * int(i)
					print("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
					os.system("echo " + str(last_rpm) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))
					print("выдаю  ",i,"%",  "горячая карта ", hot_gpu)
	elif selected_mod == 2:
		print("Выбран статичный режим")
		os.system("echo 1 >>/sys/class/hwmon/hwmon1/pwm"+str(select_fan)+"_enable")
		print("echo " + str(text["2"]) + " >> /sys/class/hwmon/hwmon1/pwm"+str(select_fan))