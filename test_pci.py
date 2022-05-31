import os, subprocess, json, time, sys, re


def applay_pci_status(server_side_pci = None):
    subprocess.run('/hive/bin/miner stop',shell=True)
    with open('pci_status_file.json', 'r') as f:  #подгружаем ранее созданный файл с данными
        pci_status_local = json.load(f)

    if server_side_pci == None:    # если запущен как инит при загрузке просто проверяем и отключаем если есть отключенные
        for i in pci_status_local:
            for k, v in i.items():
                print('текущее сотояние PCI',k,v)
                if v == False:
                    subprocess.getstatusoutput("timeout  30 sudo echo 1 > /sys/bus/pci/devices/0000:"+str(k.split(' ')[0]) +"/remove")
    else:
        for local in pci_status_local:
            for k, v in local.items():
                v_local = v
            for s_s_p in server_side_pci:
                for k, v in s_s_p.items():
                    s_s_p_v = v
            if v_local == True and s_s_p_v == False:
                subprocess.getstatusoutput("timeout  30 sudo echo 1 > /sys/bus/pci/devices/0000:"+str(k.split(' ')[0]) +"/remove")
            elif  v_local == False and s_s_p_v == True:
                subprocess.run('reboot',shell=True)
    subprocess.run('/hive/bin/miner start',shell=True)            
if __name__ == '__main__':                                                                                                                           
    applay_pci_status()     