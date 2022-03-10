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

tf  = str(os.path.getmtime(hive_conf_autofan)).split(".")[0]
dn = str(time.time()).split(".")[0]
ggc_server_set_option = ''

def communication_hive(id_rig_in_server, key_slave, rigOnBoot, const_rpm, rpmfun,rigRpmFanMaximum):
    global ggc_server_set_option

    
    if (int(tf) + 0000000100 >= int(dn)) or rigOnBoot == 0:
        print('conf_auto_fan_hive ИЗМЕНЕН или только загружен')
        conf_auto_fan_hive = open(hive_conf_autofan, "r") 
        lines = conf_auto_fan_hive.readlines()
        for line in lines:
            if "AUTO_ENABLED=" in line:
                hive_auto_fan_state = line.replace("AUTO_ENABLED=", "").replace('"', '').replace('\n', '')
                if int(hive_auto_fan_state) == 0:
                    ggc_server_set_option = 'unlock'
                else:
                    ggc_server_set_option = 'lock'
        if ggc_server_set_option == 'lock'
            #requests.get('http://ggc.center:8000/web_inteface_optionset/', data = [('rig_id', id_rig_in_server),('web_interface','lock')])
            print("хочу заблокировать на сайте")
        else:
            #requests.get('http://ggc.center:8000/web_inteface_optionset/', data = [('rig_id', id_rig_in_server),('web_interface','unlock')])
            print("хочу разблокировать на сайте")

    if rigOnBoot == 0:
        print("первый старт, забрал настройки с сервера")
        response= requests.get('http://ggc.center:8000/get_option_rig/', data = [('id_in_serv', id_rig_in_server),('key_slave',key_slave)])
        resp_server_ggc = response.json()
        manual_fan_speed = int(resp_server_ggc["data"][0]["attributes"]["SetMode2"]["SetRpm"])
        terget_temp_min = int(resp_server_ggc["data"][0]["attributes"]["SetMode0"]["terget_temp_min"])
        terget_temp_max = int(resp_server_ggc["data"][0]["attributes"]["SetMode0"]["terget_temp_max"])
        min_fan_rpm = round(int(const_rpm) / 100 * int(resp_server_ggc["data"][0]["attributes"]["SetMode0"]["min_fan_rpm"]))
        target_core = int(terget_temp_min) + (int(int(terget_temp_max) - int(terget_temp_min)))
        target_mem  = 88
        fan_mode    = int(resp_server_ggc["data"][0]["attributes"]["SetModeFan"]["selected_mod"])
        if fan_mode == 0:
            fan_mode = 2
        elif fan_mode == 2:
            fan_mode = 1
    
        wr_data = {"manual_fan_speed":manual_fan_speed, "terget_temp_min":terget_temp_min, "terget_temp_max":terget_temp_max,
                    "min_fan_rpm":min_fan_rpm,"target_core":target_core,"target_mem":target_mem, "fan_mode":fan_mode}
        jsonString = json.dumps(wr_data)
        jsonFile = open("wr.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
        print("создал дубликат настроек req_link_hive")

    else:
        with open('wr.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            manual_fan_speed = json_data['manual_fan_speed']
            terget_temp_min  = json_data['terget_temp_min']
            terget_temp_max  = json_data['terget_temp_max']
            min_fan_rpm      = json_data['min_fan_rpm']
            target_core      = json_data['target_core']
            target_mem       = json_data['target_mem']
            fan_mode         = json_data['fan_mode']
            print("проверил настройки из дубликата")


    with open(req_link_hive, 'r', encoding='utf-8') as f:
        print("захожу в проверку настроек req_link_hive")
        json_data = json.load(f)
        if (json_data['target_temp'] != target_core) or (json_data['target_mtemp'] != target_mem) 
            or (json_data['manual_fan_speed'] != manual_fan_speed) or (json_data['fan_mode'] != fan_mode)
            or(json_data['min_fan'] != min_fan_rpm):
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
            print("нужно отправить новые настройки на сервер")
            communication_hive(id_rig_in_server, key_slave, rigOnBoot=0, const_rpm, rpmfun,rigRpmFanMaximum)

    fan_persent = []
    for i in range(0,3)
        fan_persent.append((int(rpmfun)/int(rigRpmFanMaximum)) * 100)
    
    print(fan_persent)
    with open(answer_link_hive, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        json_data['casefan'] = fan_persent
        f.seek(0)
        f.write(json.dumps(json_data))
        f.truncate() 
    print("Записал данные по кулерам")

if __name__ == '__main__':                                                                                                                           
    communication_hive()