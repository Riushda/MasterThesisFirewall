obj-m = firewall.o
KVERSION = $(shell uname -r)
firewall-objs := ./src/firewall.o ./src/rule.o ./src/htable.o ./src/utils.o

all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean