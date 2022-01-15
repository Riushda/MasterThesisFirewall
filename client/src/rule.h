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

typedef struct rule_list
{
    rule_t *head;
    short index;
} rule_list_t;

int parse_ip(string_t *str_ip, int *ip, bitmask_t *bitmask);

void parse_port(string_t *str_port, short *port, bool_t *not_v);

void parse_action(string_t *str_action, bool_t *action);

void print_rule(rule_t rule);

void init_rule_list(rule_list_t *rule_list);

void insert_rule(rule_list_t *rule_list, rule_t *rule);

void remove_rule(rule_list_t *rule_list, short index);

rule_t *search_rule(rule_list_t *rule_list, short index);

void print_rule_list(rule_list_t *rule_list);

void destroy_rule_list(rule_list_t *rule_list);

#endif
