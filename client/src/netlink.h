#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>
#include <linux/netlink.h>
#include <sys/socket.h>
#include <errno.h>
#include <sys/select.h>
#include "constant.h"
#include "context_rule.h"

#ifndef NETLINK_H
#define NETLINK_H

struct sockaddr_nl src_addr;
struct sockaddr_nl dest_addr;
int sock_fd;

int open_netlink();

int receive_msg(volatile int *keeprunning);

int send_msg(char *data);

#endif