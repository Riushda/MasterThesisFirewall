#include <linux/ip.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "constant.h"

#ifndef RULE_H
#define RULE_H

enum
{
    A_RULE = 0,
    R_RULE = 1
};

struct rule
{
    uint8_t not_src;
    __be32 src;
    int src_bm;
    uint8_t not_dst;
    __be32 dst;
    int dst_bm;
    uint8_t not_sport;
    __be16 sport;
    uint8_t not_dport;
    __be16 dport;
};

int parse_ip(unsigned char *str_ip, __be32 *ip, int *bitmask);

void parse_port(unsigned char *str_port, __be16 *port, uint8_t *not_v);

void print_rule(struct rule rule);

#endif
