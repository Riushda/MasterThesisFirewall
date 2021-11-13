FROM ubuntu:20.04
USER root
RUN apt-get update && apt-get install -y apt-utils iptables net-tools iputils-ping iproute2 traceroute mosquitto
RUN update-alternatives --set ip6tables /usr/sbin/ip6tables-nft