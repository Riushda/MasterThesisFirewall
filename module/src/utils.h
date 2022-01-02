#include <linux/kernel.h>

#ifndef UTILS_H
#define UTILS_H

#define NETLINK_FW 17
#define TABLE_SIZE 1024
#define RULE_SIZE 12

void print_bits(size_t const size, void const *const ptr);

#endif