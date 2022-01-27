#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <linux/netlink.h>
#include <sys/socket.h>
#include <errno.h>
#include <sys/select.h>
#include "context_rule.h"
#include "rule.h"
#include "constant.h"

#ifndef NETLINK_H
#define NETLINK_H

struct sockaddr_nl src_addr;
struct sockaddr_nl dest_addr;
int sock_fd;

int open_netlink();

int receive_msg(volatile int *keeprunning);

int send_msg(uint8_t code, void *data);

#endif