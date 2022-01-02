#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/udp.h>

#ifndef RULE_H
#define RULE_H

struct rule
{
    __be32 src;
    __be32 dst;
    __be16 sport;
    __be16 dport;
};

void parse_to_rule(struct sk_buff *skb, struct rule *rule);

int parse_to_buffer(struct sk_buff *skb, unsigned char *buffer);

void rule_to_buffer(struct rule *rule, unsigned char *buffer);

void print_rule(struct rule *rule);

#endif