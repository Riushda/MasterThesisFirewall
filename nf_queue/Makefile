TARGET = nf-queue
LIBS = -lmnl -lnetfilter_queue  -lnftnl
CC = gcc
CFLAGS = -g3 -ggdb -Wall 

.PHONY: default all clean start stop

default: $(TARGET)
all: default

OBJECTS = $(patsubst %.c, %.o, $(wildcard **/*.c))
HEADERS = $(wildcard **/*.h)

%.o: %.c $(HEADERS)
	$(CC) $(CFLAGS) -c $< -o $@

$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -Wall $(LIBS) -o $@

start : 
	(sleep 2; sudo iptables -A INPUT -j NFQUEUE --queue-num 0) & 
	sudo ./nf-queue 0

stop :
	sudo iptables -D INPUT -j NFQUEUE --queue-num 0

clean:
	-rm -f *.o
	-rm -f $(TARGET)