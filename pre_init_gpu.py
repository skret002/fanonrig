import subprocess, re, json

def f_init_gpu():
    work_pci = []                                                    
    (status,output_fan)=subprocess.getstatusoutput("sudo lspci -v | grep --color -E '(VGA|3D)'")
    all_pci = re.split('\n', output_fan)
    for i in all_pci:
        if "VGA controller" not in str(i.split('[', 1)[1].split(']')[0]):  
            name = str(i.split('[', 1)[1].split(']')[0]).replace('RTX','').replace('NVIDIA','').replace('AMD','').replace('GeForce','').replace('NVIDIA','').replace('/Max-Q','').replace(' ','').replace("''",'')           
            if name == '/ATI':
                name = 'AMD ' + str(i.split('[')[2].split(']')[0].replace('Radeon','').replace('RX','').replace(' ','')[0:3].replace('/',''))
            work_pci.append({str(i.split(' ')[0])+' ('+str(name)+')': True})
    with open('/home/fanonrig/init_gpu.json', "w+") as file:
        file.seek(0)
        file.write(json.dumps(work_pci))
        file.truncate() 
        
if __name__ == '__main__':                                                                                                                           
    f_init_gpu()  