import subprocess, json, time

def test(ser_side_info):
    with open('/home/fanonrig/init_gpu.json', 'r') as f:
        f_init_gpu = json.load(f)  
    obj1 = []                                                       
    obj2 = []                                               
    for i in range(0, len(f_init_gpu)):
        for key,value in f_init_gpu[i].items():
            obj1.append(key)                                                  
    for i in range(0, len(ser_side_info)):
        for key,value in ser_side_info[i].items():
            obj2.append(key)    
    print(obj1, '\n', obj2)
    for i in obj1:
        non_change = 1
        if i in obj2:
            non_change = 0
        if non_change != 0:
            print("карты в слотах изменились")
            return(False) 

def applay_pci_status(server_side_pci = None):
    if server_side_pci != None:
        if test(server_side_pci) == False:
            return(False)
    try:
        subprocess.run('/hive/bin/miner stop',shell=True)
        time.sleep(3)
        with open('/home/fanonrig/pci_status_file.json', 'r') as f:  #подгружаем ранее созданный файл с данными
            pci_status_local = json.load(f)
    
        if server_side_pci == None:    # если запущен как инит при загрузке просто проверяем и отключаем если есть отключенные
            for i in pci_status_local:
                for k, v in i.items():
                    print('текущее сотояние PCI',k,v)
                    if v == False or v == 'False':
                        subprocess.getstatusoutput("timeout  90 sudo echo 1 > /sys/bus/pci/devices/0000:"+str(k.split(' ')[0]) +"/remove")
        else:
            reboot = 0
            for s_s_p in server_side_pci:
                for k, v in s_s_p.items():
                    if v == False or v == 'False':
                        for local in pci_status_local:
                            for k2, v2 in local.items():
                                if k == k2:
                                    print("ОТКЛЮЧАЮ GPU", k)
                                    subprocess.getstatusoutput("timeout  30 sudo echo 1 > /sys/bus/pci/devices/0000:"+str(k.split(' ')[0]) +"/remove")
                    if v == True or v == 'True': 
                        for local in pci_status_local:
                            adder = 1
                            for k2, v2 in local.items():
                                    if k == k2:
                                        adder = 0
                        
                        if adder == 1:
                            reboot = 1
                            pci_status_local.append({k:v})
                            with open('/home/fanonrig/init_gpu.json', "w+") as file:
                                file.seek(0)
                                file.write(json.dumps(pci_status_local))
                                file.truncate() 
            if reboot == 1:
                print("Некоторые карты приказано включить, ухожу на перезагрузку")
                
        subprocess.run('/hive/bin/miner start',shell=True)        
    except Exception as e:
        print(e)
         
if __name__ == '__main__':                                                                                                                           
    applay_pci_status()     