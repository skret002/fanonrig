import json 
import simplejson
import os
import requests
import time
import sys
from testFan import testFan
from handler_messeges import transmit_mess as send_mess
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

        with open(req_link_hive, 'r') as f:
            print("захожу в проверку настроек req_link_hive")
            json_data = json.load(f)
            j_target_temp      = int(json_data['target_temp'])
            j_target_mtemp     = int(json_data['target_mtemp'])
            j_manual_fan_speed = int(json_data['manual_fan_speed'])
            j_fan_mode         = int(json_data['fan_mode'])
            if j_fan_mode == 2:
                j_fan_mode = 0
            else:
                j_fan_mode = 2
            j_min_fan          = int(json_data['min_fan'])
            print(j_target_temp, j_target_mtemp, j_manual_fan_speed, j_fan_mode, j_min_fan)
            print(int(now_target_core), int(now_target_mem), int(now_manual_fan_speed), int(now_fan_mode), int(now_min_fan_rpm))
            if (j_target_temp != int(now_target_core)) or (j_target_mtemp != int(now_target_mem)) or (j_manual_fan_speed != int(now_manual_fan_speed)) or (j_fan_mode != int(now_fan_mode)) or (j_min_fan != int(now_min_fan_rpm)):
                print("настройки не одинаковые req_link_hive")
                if int(str(j_target_temp)[1:2]) == 0:
                    new_min_temp =  j_target_temp - 10
                    new_max_temp =  j_target_temp + 10
                else:
                    new_min_temp =  j_target_temp - int(str(j_target_temp)[1:2])
                    new_max_temp =  j_target_temp + int(str(j_target_temp)[1:2])
                new_target_mem = j_target_mtemp
                new_manual_fan_speed = j_manual_fan_speed
                fan_mode = j_fan_mode
                min_fan = j_min_fan
                print("нужно отправить новые настройки на сервер",new_min_temp, new_max_temp,new_target_mem, new_manual_fan_speed,fan_mode,min_fan)
                new_data = [('rig_id', id_rig_in_server),('new_min_temp',new_min_temp),('new_max_temp',new_max_temp),('new_target_mem',new_target_mem),('new_manual_fan_speed',new_manual_fan_speed),('fan_mode',fan_mode),('min_fan',min_fan)]
                requests.get('http://ggc.center:8000/set_option_for_hive/', data = new_data,stream=True, timeout=10)
            else:
                print('настройки хайва и сервера одинаковые')
        if os.path.exists(req_recallibrate) == True:
            print("начать реколебровку") 
            send_mess(' Запуск реколебровки внешних кулеров, ожидайте результата. Это может занять около 5 мин.', id_rig_in_server)                                                                                                            
            res_test_fan = testFan(id_rig_in_server)                                                                                                 
            os.system("rm " + req_recallibrate)
            os.system("rm " +  answer_recallibrate )                                                                                                 
            file_info = open(answer_recallibrate, "w+")                                                                                              
            file_info.write(str(res_test_fan))                                                                                                       
            file_info.close() 
    else:
        pass

    write_resp(rpmfun, rigRpmFanMaximum)

    return(True)

if __name__ == '__main__':                                                                                                                           
    communication_hive()