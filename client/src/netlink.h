#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <linux/netlink.h>
#include <sys/socket.h>
#include <errno.h>
#include "constant.h"

#ifndef NETLINK_H
#define NETLINK_H

int open_netlink();

void close_netlink();

int send_msg(uint8_t code, void *data, short data_len);

#endif