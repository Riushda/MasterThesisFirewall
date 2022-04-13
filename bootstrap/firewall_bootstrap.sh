#!/usr/bin/env bash

echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf > /dev/null
echo "net.ipv4.conf.all.accept_redirects=0" | sudo tee -a /etc/sysctl.conf > /dev/null
echo "net.ipv4.conf.default.accept_redirects=0" | sudo tee -a /etc/sysctl.conf > /dev/null
echo "net.ipv4.conf.all.send_redirects=0" | sudo tee -a /etc/sysctl.conf > /dev/null
echo "net.ipv4.conf.default.send_redirects=0" | sudo tee -a /etc/sysctl.conf > /dev/null
echo "net.ipv4.conf.eth1.send_redirects=0" | sudo tee -a /etc/sysctl.conf > /dev/null
echo "set -g mouse on" | tee .tmux.conf > /dev/null
sudo dnf install -y make automake gcc python3-devel python3-nftables libnetfilter_queue-devel pip tmux nano graphviz graphviz-devel
sudo pip install NetfilterQueue Pyro4 Cython transitions schedule scapy numpy aenum graphviz pygraphviz
