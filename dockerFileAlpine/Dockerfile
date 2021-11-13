FROM trafex/alpine-mosquitto
USER root
RUN echo -e "http://nl.alpinelinux.org/alpine/v3.11/main\nhttp://nl.alpinelinux.org/alpine/v3.11/community" > /etc/apk/repositories
RUN su && apk update && apk add tcptraceroute iproute2 tcpdump