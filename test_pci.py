import subprocess, json, time


def applay_pci_status(server_side_pci = None):
    try:
        subprocess.run('/hive/bin/miner stop',shell=True)
        time.sleep(30)
        with open('/home/fanonrig/pci_status_file.json', 'r') as f:  #подгружаем ранее созданный файл с данными
            pci_status_local = json.load(f)
    
        if server_side_pci == None:    # если запущен как инит при загрузке просто проверяем и отключаем если есть отключенные
            for i in pci_status_local:
                for k, v in i.items():
                    print('текущее сотояние PCI',k,v)
                    if v == False or v == 'False':
                        subprocess.getstatusoutput("timeout  90 sudo echo 1 > /sys/bus/pci/devices/0000:"+str(k.split(' ')[0]) +"/remove")
        else:
            for local in pci_status_local:
                for k, v in local.items():
                    v_local = v
                for s_s_p in server_side_pci:
                    for k, v in s_s_p.items():
                        s_s_p_v = v
                if v_local == True and s_s_p_v == False or v_local == 'True' and s_s_p_v == 'False':
                    subprocess.getstatusoutput("timeout  90 sudo echo 1 > /sys/bus/pci/devices/0000:"+str(k.split(' ')[0]) +"/remove")
                elif  v_local == False and s_s_p_v == True or  v_local == 'False' and s_s_p_v == 'True':
                    subprocess.run('reboot',shell=True)
        time.sleep(30)
        subprocess.run('/hive/bin/miner start',shell=True)        
    except Exception:
        pass    
if __name__ == '__main__':                                                                                                                           
    applay_pci_status()     