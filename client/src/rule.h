#include <arpa/inet.h>
#include "constant.h"
#include "utils.h"

#ifndef RULE_H
#define RULE_H

typedef struct rule
{
    int src;
    int dst;
    short sport;
    short dport;
    bitmask_t src_bm;
    bitmask_t dst_bm;
    bool_t not_src;
    bool_t not_dst;
    bool_t not_sport;
    bool_t not_dport;
    proto_t proto;
    bool_t action;
    short index;
    struct rule *next;
} rule_t;

int parse_ip(string_t *str_ip, int *ip, bitmask_t *bitmask);

void parse_port(string_t *str_port, short *port, bool_t *not_v);

void print_rule(rule_t rule);

#endif
