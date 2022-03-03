# Readme

## Install rawhide package

sudo yum install fedora-repos-rawhide
sudo yum install --enablerepo rawhide libnetfilter_queue-devel-1.0.5
sudo yum install libmnl-devel
sudo yum install libnftnl-devel

This should install necessary packages but it is possible that some are missing.

## Compile the code

gcc -g3 -ggdb -Wall -lmnl -lnetfilter_queue -o nf-queue nf-queue.c

Then start the program:

sudo ./nf-queue 0

The parameter indicates the listening queue.

## Setup iptables

! WARNING ! This command should be used only when nf-queue is running otherwise ssh will not work anymore.

sudo iptables -A INPUT -j NFQUEUE --queue-num 0
sudo iptables -A OUTPUT -j NFQUEUE --queue-num 0
sudo iptables -A FORWARD -j NFQUEUE --queue-num 0

This redirects all traffic to queue 0, it is possible to specify a specific interface with -i.

To safely stop the code you should first delete the rule:

sudo iptables -D INPUT -j NFQUEUE --queue-num 0
sudo iptables -D OUTPUT -j NFQUEUE --queue-num 0
sudo iptables -D FORWARD -j NFQUEUE --queue-num 0

# python client requirements 

sudo dnf install python3-nftables
sudo pip3 install jsonschema

## Some nftables commands

sudo nft add table ip filter : create a table of type ip and name filter (automatically created by the iptables command)

sudo nft 'add chain ip filter input { type filter hook input priority 0 ; }' : create an input chain in the table of type ip and name filter

sudo nft list tables : show name and type of all tables
sudo nft list table filter : show all the chains and rules inside the table filter

sudo nft add rule filter INPUT tcp dport 22 mark set 82 : add a marker integer 82 to all packet with destination port 22, in the chain INPUT in the table filter

sudo nft add rule filter OUTPUT tcp sport 22 mark set 82 : add a marker integer 82 to all packet with source port 22, in the chain OUTPUT in the table filter

sudo nft add rule filter OUTPUT tcp sport 22 counter mark set 82 : same command than previous one but has a counter to check how many packets matched, useful to debug rules

sudo nft -n -a list ruleset : to list all rules with their handle (index)

sudo nft delete rule filter OUTPUT handle 11 : delete rule of handle (index) 11 in the chain OUTPUT in the table filter

sudo nft flush ruleset : remove all rules, chains and tables


