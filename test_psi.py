import os
import subprocess
import requests
import time
import sys
import subprocess
import re


work_pci = []
(status,output_fan)=subprocess.getstatusoutput("sudo lspci -v | grep --color -E '(VGA|3D)'")
all_pci = re.split('\n', output_fan)
for i in all_pci:
    work_pci.append({i.split(' ')[0]: False})
print(work_pci)