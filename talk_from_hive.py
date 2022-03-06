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


def communication_hive(id_rig_in_server, key_slave, rigOnBoot):
    overwriting = rigOnBoot

    resp_server_ggc = requests.get('http://ggc.center:8000/get_option_rig/', data = [('id_in_serv', id_rig_in_server),('key_slave',key_slave)])
    manual_fan_speed = int(resp_server_ggc["data"][0]["attributes"]["SetMode2"]["SetRpm"])
    terget_temp_min = int(resp_server_ggc["data"][0]["attributes"]["SetMode0"]["terget_temp_min"])
    terget_temp_max = int(resp_server_ggc["data"][0]["attributes"]["SetMode0"]["terget_temp_max"])
    min_fan_rpm = round(int(const_rpm) / 100 * int(resp_server_ggc["data"][0]["attributes"]["SetMode0"]["min_fan_rpm"]))
    target_core = round(int(terget_temp_max) - int(terget_temp_min))
    target_mem  = 88
    fan_mode    = int(resp_server_ggc["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
    if fan_mode == 0:
        fan_mode = 2
    elif fan_mode == 2:
        fan_mode = 1

    if rigOnBoot == 1:
        with open(req_link_hive, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            if (json_data['target_temp'] != target_core) or (json_data['target_mtemp'] != target_mem) 
                or (json_data['manual_fan_speed'] != manual_fan_speed) or (json_data['fan_mode'] != fan_mode)
                or(json_data['min_fan'] != min_fan_rpm):
                overwriting = 0


    if overwriting == 0:
        with open(req_link_hive, 'r+') as f: 
            json_data = json.load(f)
            json_data['target_temp'] = target_core
            json_data['target_mtemp'] = target_mem
            json_data['manual_fan_speed'] = manual_fan_speed
            json_data['fan_mode'] = fan_mode
            json_data['min_fan'] = min_fan_rpm
            json_data['max_fan'] = 100
            f.seek(0)                                                                                                                 
            f.write(json.dumps(json_data))                                                                                            
            f.truncate()


if __name__ == '__main__':                                                                                                                           
    communication_hive()    