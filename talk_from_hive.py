import json 
import simplejson
import os
import requests
import time
import sys

req_link_hive       = '/run/hive/fan_controller_req'  #файл запроса в хайв json
answer_link_hive    = '/run/hive/fan_controller_rsp' # файл ответа из hive json
req_recallibrate    = '/run/hive/fan_controller_recallibrate_req' # запрос реколибровки если файл есть > потом удалить
answer_recallibrate ='/run/hive/fan_controller_recallibrate_rsp' # вывести рез. реколиб. текстом
hive_conf_autofan   = '/hive-config/ykeda_autofan.conf' # основной конфиг автофана

def write_resp(rpmfun, rigRpmFanMaximum):
    fan_persent = []
    try:                                                                                                                                             
        for i in range(0,4):                                                                                                                         
            fan_persent.append(round((int(rpmfun)/int(rigRpmFanMaximum)) * 100))                                                                     
                                                                                                                 
        data= {"casefan":fan_persent, "thermosensors": [-5, 30]}                                                                                     
        jsonString = json.dumps(data)                                                                                                                
        jsonFile = open(answer_link_hive, "w")                                                                                                       
        jsonFile.write(jsonString)                                                                                                                   
        jsonFile.close()                                                                                                                             
    except Exception as e:                                                                                                                           
        print(e)                            
    print("Записал данные по кулерам")
    return()

def communication_hive(id_rig_in_server, key_slave, mod_option_hive, const_rpm, rpmfun,rigRpmFanMaximum, option2, terget_temp_min,terget_temp_max, min_fan_rpm, target_mem_temp, selected_mod):
    if mod_option_hive == 1:
        now_manual_fan_speed = option2
        now_terget_temp_min = terget_temp_min
        now_terget_temp_max = terget_temp_max
        now_min_fan_rpm = min_fan_rpm
        now_target_core = int(int(terget_temp_min) + (int(int(terget_temp_max) - int(terget_temp_min))/2))
        now_target_mem  = target_mem_temp
        now_fan_mode    = selected_mod
        if now_fan_mode == 0:
            fan_mode = 2
        elif now_fan_mode == 2:
            fan_mode = 1

        with open(req_link_hive, 'r', encoding='utf-8') as f:
            print("захожу в проверку настроек req_link_hive")
            json_data = json.load(f)
            if (json_data['target_temp'] != now_target_core) or (json_data['target_mtemp'] != now_target_mem) or (json_data['manual_fan_speed'] != now_manual_fan_speed) or (json_data['fan_mode'] != now_fan_mode) or (json_data['min_fan'] != now_min_fan_rpm):
                print("настройки не одинаковые req_link_hive")
                new_min_temp =  int(json_data['target_temp']) - int(str(json_data['target_temp'])[:1])
                new_max_temp =  int(json_data['target_temp']) + int(str(json_data['target_temp'])[:1])
                new_target_mem = json_data['target_mtemp']
                new_manual_fan_speed = json_data['manual_fan_speed']
                fan_mode = json_data['fan_mode']
                if fan_mode == 2:
                    fan_mode = 0
                elif fan_mode == 1:
                    fan_mode = 2
                min_fan = json_data['min_fan']
            print("нужно отправить новые настройки на сервер",new_min_temp, new_max_temp,new_target_mem, new_manual_fan_speed,fan_mode,min_fan)


    write_resp(rpmfun, rigRpmFanMaximum)

if __name__ == '__main__':                                                                                                                           
    communication_hive()