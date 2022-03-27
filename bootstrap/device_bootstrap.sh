#!/usr/bin/env bash

echo "net.ipv4.conf.all.accept_redirects=0" | sudo tee -a /etc/sysctl.conf > /dev/null
echo "net.ipv4.conf.default.accept_redirects=0" | sudo tee -a /etc/sysctl.conf > /dev/null
sudo apk add tcptraceroute nano mosquitto-clients py3-paho-mqtt
sudo rc-update add staticroute
sudo echo "net 192.168.33.0 netmask 255.255.255.0 gw 192.168.33.10" | sudo tee -a /etc/route.conf > /dev/null


