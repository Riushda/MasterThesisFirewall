obj-m = firewall.o
KVERSION = $(shell uname -r)

SRC_DIRS := $(PWD)/src

# find all .c file
SRCS := $(shell find $(SRC_DIRS) -name '*.c')

# replace .c by .o
firewall-objs := $(SRCS:.c=.o) 
# remove prefix of absolute path until src
firewall-objs := $(firewall-objs:${PWD}/%=%)

.PHONY: all test clean

all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules

stop :
	-sudo rmmod firewall
	
clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean
	-sudo rmmod firewall

test:
	-sudo rmmod firewall
    # Clear the kernel log without echo
	sudo dmesg -C
    # Insert the module 
	
	sudo insmod firewall.ko
	
    # Display the kernel log
	dmesg --follow