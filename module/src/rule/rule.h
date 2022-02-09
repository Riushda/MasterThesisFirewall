#include "../protocol/abstract_packet.h"
#include "htable.h"
#include "trie.h"

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
} rule_t;

/* USER */

int parse_ip(string_t *str_ip, int *ip, bitmask_t *bitmask);

void parse_port(string_t *str_port, short *port, bool_t *not_v);

void print_rule(rule_t rule);

/* KERNEL */

/* SKB */

int rule_to_buffer(rule_t *rule, unsigned char *buffer);

/* RULE STRUCTURE */

typedef struct rule_structure
{
    trie_t *src_trie;
    trie_t *dst_trie;
    h_table_t *sport_table;
    h_table_t *dport_table;
    data_constraint_t *data_c;
    vector_t actions[VECTOR_SIZE];
} rule_struct_t;

int init_rules(rule_struct_t *rule_struct);

int insert_rule(rule_struct_t *rule_struct, rule_t rule);

int insert_rule_and_constraint(rule_struct_t *rule_struct, rule_t rule, char *buf);

int remove_rule(rule_struct_t *rule_struct, rule_t rule);

int match_rule(rule_struct_t *rule_struct, abstract_packet_t *packet);

int match_constraint(rule_struct_t *rule_struct, abstract_packet_t *packet);

void destroy_rules(rule_struct_t *rule_struct);

#endif
