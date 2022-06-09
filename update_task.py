import os
import subprocess
import requests
from handler_messeges import transmit_mess as send_mess
import time
import json


def task_update(rig_id, soft_rev):
    ver = soft_rev
    response = requests.post('http://ggc.center:8000/soft_revison/', data = {'id_rig': rig_id})
    url = response.json()["data"]["url"]
    new_ver = response.json()["data"]["version"]
    if str(ver) != str(new_ver):
        os.system("wget -O fanonrig.zip "+ url)
        #print(url, new_ver)
        os.system("unzip -o fanonrig.zip")
        os.system("rm fanonrig.zip")
        send_mess(' GPU GOD CONTROL updated to version ' + str(new_ver), rig_id)
        with open('settings.json', 'r+') as f:
            json_data = json.load(f)                                                                                                  
            json_data['soft_rev'] = str(new_ver)                                                                                                                                                                                 
            f.seek(0)                                                                                                                 
            f.write(json.dumps(json_data))                                                                                            
            f.truncate()  
        time.sleep(3)
        print("*********** SYSTEM UPDATED ****************")
        os.system("reboot")
        subprocess.run(['reboot'], stdout=subprocess.PIPE)

if __name__ == '__main__':
    task_update()