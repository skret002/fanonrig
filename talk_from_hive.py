import json 
import simplejson
import os
import requests
import time
import sys
from testFan import testFan
from engine import testing
from handler_messeges import transmit_mess as send_mess
req_link_hive       = '/run/hive/fan_controller_req'  #файл запроса в хайв json
answer_link_hive    = '/run/hive/fan_controller_rsp' # файл ответа из hive json
req_recallibrate    = '/run/hive/fan_controller_recallibrate_req' # запрос реколибровки если файл есть > потом удалить
answer_recallibrate ='/run/hive/fan_controller_recallibrate_rsp' # вывести рез. реколиб. текстом
hive_conf_autofan   = '/hive-config/ykeda_autofan.conf' # основной конфиг автофана
fan_diagn_report    = '/run/hive/fan_controller_report_req' #при запросе пользователем отчёта будет создан пустой файл
hive_dir            = '/hive-config/'


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

def communication_hive(id_rig_in_server, key_slave, mod_option_hive, const_rpm, rpmfun,rigRpmFanMaximum, option2, terget_temp_min,terget_temp_max, min_fan_rpm, target_mem_temp, selected_mod, device_name):
    if os.path.exists(hive_dir+str(device_name)+'.wtt') == False:
        send_mess(str(device_name)+' -подключен к Hive OS, "краткий" мониторинг так же доступен в интерфейсе Hive', id_rig_in_server)                                                                                                 
        file_info = open(hive_dir+str(device_name)+'.wtt', "w+")                                                                                              
        file_info.write('WIND TANK TECHNOLOGIES L.L.C'+ '\n' +'Model: '+ str(device_name)  + '\n' +  '@ designed by Alexander Mevlutov')                                                                                                       
        file_info.close()     

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
            file_info.write('device_name' + '\n' + str(res_test_fan))                                                                                                       
            file_info.close() 
        if os.path.exists(fan_diagn_report) == True:
            print("Запрос диагностики") 
            send_mess(' Запрос диагностики из Hive OS', id_rig_in_server)                                                                                                 
            os.system("rm " + fan_diagn_report)
                                                                                                
            file_info = open(fan_diagn_report, "w+") 
            test_box_rsp = testing()
            if test_box_rsp == True:
                file_info.write('Company: WIND TANK TECHNOLOGIES L.L.C' + '\n' +'Model: '+ str(device_name)  + '\n' + 'Diagnostics completed successfully' + '\n' + '@ designed by Alexander Mevlutov')    
                send_mess(' Company: WIND TANK TECHNOLOGIES L.L.C' + '\n' +'Model: '+ str(device_name)  + '\n' + 'Diagnostics completed successfully' + '\n' + '@ designed by Alexander Mevlutov', id_rig_in_server)  
            else:
                file_info.write('Company: WIND TANK TECHNOLOGIES L.L.C' + '\n' +'Model: '+ str(device_name)  + '\n' + str(test_box_rsp) + '\n' + '@ designed by Alexander Mevlutov')                                                                                               
                send_mess(' Company: WIND TANK TECHNOLOGIES L.L.C' + '\n' +'Model: '+ str(device_name)  + '\n' + str(test_box_rsp) + '\n' + '@ designed by Alexander Mevlutov', id_rig_in_server)
            file_info.close() 
    else:
        pass

    write_resp(rpmfun, rigRpmFanMaximum)

    return(True)

if __name__ == '__main__':                                                                                                                           
    communication_hive()