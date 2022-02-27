# Readme

## Install rawhide package

sudo yum install fedora-repos-rawhide
sudo yum install --enablerepo rawhide libnetfilter_queue-devel-1.0.5

This should install necessary packages but it is possible that some are missing.

## Compile the code

gcc -g3 -ggdb -Wall -lmnl -lnetfilter_queue -o nf-queue nf-queue.c

Then start the program:

sudo ./nf-queue 0

The parameter indicates the listening queue.

## Setup iptables

! WARNING ! This command should be used only when nf-queue is running otherwise ssh will not work anymore.

sudo iptables -A INPUT -j NFQUEUE --queue-num 0

This redirects all traffic to queue 0, it is possible to specify a specific interface with -i.

To safely stop the code you should first delete the rule:

sudo iptables -D INPUT -j NFQUEUE --queue-num 0