obj-m = firewall.o
KVERSION = $(shell uname -r)
firewall-objs := ./src/firewall.o ./src/rule.o ./src/trie.o ./src/htable.o ./src/linked_list.o ./src/utils.o ./src/constant.h

# Thanks to Job Vranish (https://spin.atomicobject.com/2016/08/26/makefile-c-projects/)
TARGET_EXEC := client.out

BUILD_DIR := ./build
SRC_DIRS := ./src

# Find all the C and C++ files we want to compile
# Note the single quotes around the * expressions. Make will incorrectly expand these otherwise.
SRCS := $(shell find $(SRC_DIRS) -name '*.c')

# String substitution for every C/C++ file.
# As an example, hello.cpp turns into ./build/hello.cpp.o
OBJS := $(SRCS:%=$(BUILD_DIR)/%.o)

# String substitution (suffix version without %).
# As an example, ./build/hello.cpp.o turns into ./build/hello.cpp.d
DEPS := $(OBJS:.o=.d)

# Every folder in ./src will need to be passed to GCC so that it can find header files
INC_DIRS := $(shell find $(SRC_DIRS) -type d)
# Add a prefix to INC_DIRS. So moduleA would become -ImoduleA. GCC understands this -I flag
INC_FLAGS := $(addprefix -I,$(INC_DIRS))

# The -MMD and -MP flags together generate Makefiles for us!
# These files will have .d instead of .o as the output.
CPPFLAGS := $(INC_FLAGS) -MMD -MP

# Build step for C source
$(BUILD_DIR)/%.c.o: %.c
	mkdir -p $(dir $@)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

.PHONY: all test clean

all:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) modules
	
clean:
	make -C /lib/modules/$(KVERSION)/build M=$(PWD) clean
	rm -r $(BUILD_DIR)
	rm $(TARGET_EXEC)
	-sudo rmmod firewall

test:
	-sudo rmmod firewall
    # Clear the kernel log without echo
	sudo dmesg -C
    # Insert the module
	sudo insmod firewall.ko
    # Display the kernel log
	dmesg

-include $(DEPS)