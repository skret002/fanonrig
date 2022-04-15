#!/bin/bash
sleep 2
echo 1 >>/sys/class/hwmon/hwmon1/pwm2_enable
echo 15 >> /sys/class/hwmon/hwmon1/pwm2
sleep 10
cd /home/onrig/
sleep 90
sudo chmod ugo+x engine.bin
sudo nice -n -20 ./engine.bin
