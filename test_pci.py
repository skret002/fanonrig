import subprocess, json, time, os

def test(ser_side_info):                                      
    try:
        with open('/home/fanonrig/init_gpu.json', 'r') as f:
            f_init_gpu = json.load(f)
        obj2 = []
        for i in range(0, len(ser_side_info)):
            for key,value in ser_side_info[i].items():
                obj2.append(key.replace(' ',''))
        print(f_init_gpu, '\n', obj2)
        for i in f_init_gpu:
            non_change = 1
            if i in obj2:
                non_change = 0
            if non_change != 0:
                print("карты в слотах изменились")
                return(False)
        if len(f_init_gpu) > len(obj2):
            print("карты изменились", len(f_init_gpu), len(obj2))
            return(False)
    except Exception as e:
        print(e)  
        
def applay_pci_status(server_side_pci = None):
    if os.path.exists("/home/fanonrig/pci_status_file.json") == False and server_side_pci != None:
        print('Первый запус, создаю статус файл')
        newlocal = []
        for s_s_p in server_side_pci:
            for k, v in s_s_p.items():
                if v == False or v == 'False':
                    newlocal.append({k:v})
                if v == True or v == 'True':
                    newlocal.append({k:v})
        with open('/home/fanonrig/pci_status_file.json', "w+") as file: # Записываю новый файл состояния
            file.seek(0)                                                    
            file.write(json.dumps(newlocal)) 
            file.truncate()
            
    if server_side_pci != None:
        if test(server_side_pci) == False:
            return(False)       
    if os.path.exists("/home/fanonrig/pci_status_file.json") == False and server_side_pci == None:
        print('Это первый запуск, управление PCI не возможен')
        return()                                                        
    with open('/home/fanonrig/pci_status_file.json', 'r') as f:  #подгружаем ранее созданный файл с данными 
        pci_status_local = json.load(f)
    if server_side_pci == None:    # если запущен как инит при загрузке просто проверяем и отключаем если есть отключенные
        for i in pci_status_local:
            for k, v in i.items():
                print('текущее сотояние PCI',k,v)
                if v == False or v == 'False':
                    print('Отключаю', str(k.strip().split(' ')[0]))
                    time.sleep(5)
                    subprocess.getstatusoutput("timeout  90 sudo echo 1 > /sys/bus/pci/devices/0000:"+str(k.strip().split(' ')[0]) +"/remove")
    else:  
        #subprocess.run('/hive/bin/miner stop',shell=True)                                                    
        count_gpu_on = 0 
        reboot=0
        count_gpu_on2 = 0
        for i in pci_status_local:
            for k, v in i.items():
                if v == True or v == 'True':
                    count_gpu_on2 = count_gpu_on2 + 1
        newlocal = []
        for s_s_p in server_side_pci:
            for k, v in s_s_p.items():
                if v == False or v == 'False':
                    newlocal.append({k:v})
                    print("ОТКЛЮЧАЮ GPU", k)
                    for local in pci_status_local:
                        for k2, v2 in local.items():
                            if str(k).strip() == str(k2).strip():
                                print("local",k2, v2)
                                print('naw', k, v)
                                if str(v2).strip() != str(v).strip():
                                    reboot = 1
                                #subprocess.getstatusoutput("timeout  30 sudo echo 1 > /sys/bus/pci/devices/0000:"+str(k.split(' ')[0]) +"/remove")
                if v == True or v == 'True':
                    count_gpu_on = count_gpu_on + 1
                    newlocal.append({k:v})
        subprocess.getstatusoutput("rm /home/fanonrig/pci_status_file.json") # удаляю старый файл состояния
        with open('/home/fanonrig/pci_status_file.json', "w+") as file: # Записываю новый файл состояния
            file.seek(0)                                                    
            file.write(json.dumps(newlocal)) 
            file.truncate()
        if count_gpu_on > count_gpu_on2 or reboot == 1:           
            print("Некоторые карты приказано включить или выключить, ухожу на перезагрузку")         
            print("REBOOT")        
            subprocess.getstatusoutput("reboot")                                                

if __name__ == '__main__':                                                                                                                           
    applay_pci_status()     
