#!/usr/bin/env bash

echo "net.ipv4.conf.all.accept_redirects=0" | sudo tee -a /etc/sysctl.conf > /dev/null
echo "net.ipv4.conf.default.accept_redirects=0" | sudo tee -a /etc/sysctl.conf > /dev/null
sudo dnf install -y tcptraceroute nano mosquitto pip
pip install paho-mqtt aiocoap

sudo echo "192.168.33.0/28 via 192.168.33.10 dev eth1" | sudo tee /etc/sysconfig/network-scripts/route-eth1 > /dev/null