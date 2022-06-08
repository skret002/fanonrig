import subprocess,time
def main():
    while 1 > 0:
        time.sleep(90)
        (status,output1)=subprocess.getstatusoutput("systemctl status fan | grep Active")  
        (status,output2)=subprocess.getstatusoutput("systemctl status autofan | grep Active")  
        if 'Active: active' in output1 or 'Active: active' in output2:
            print("Autofan works")
        else:
            subprocess.getstatusoutput("sudo systemctl restart fan || sudo systemctl restart autofan")
            print("**** Restart autofan ****")
        

if __name__ == '__main__':
    main()