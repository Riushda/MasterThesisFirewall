#include "constant.h"
#include "utils.h"
#include "rule.h"

#ifndef NETLINK_H
#define NETLINK_H

int parse_to_buffer(struct sk_buff *skb, unsigned char *buffer);

void parse_to_rule(struct sk_buff *skb, rule_t *rule);

#endif
