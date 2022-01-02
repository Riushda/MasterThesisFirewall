#include "rule.h"

void parse_to_rule(struct sk_buff *skb, struct rule *rule)
{
    struct iphdr *iph;
    struct tcphdr *tcph;

    memset(rule, 0, sizeof(struct rule));
    
    iph = ip_hdr(skb);

    if (iph->protocol == IPPROTO_TCP)
    {
        tcph = tcp_hdr(skb);
        memcpy(&rule->src, &iph->saddr, sizeof(rule->src));
        memcpy(&rule->dst, &iph->daddr, sizeof(rule->dst));
        memcpy(&rule->sport, &tcph->source, sizeof(rule->sport));
        memcpy(&rule->dport, &tcph->dest, sizeof(rule->dport));
    }
}

void rule_to_buffer(struct rule *rule, unsigned char *buffer)
{
    int offset;
    offset = 0;

    memset(buffer, 0, sizeof(struct rule));

    memcpy(buffer + offset, &rule->src, sizeof(rule->src));
    offset += sizeof(rule->src);
    memcpy(buffer + offset, &rule->dst, sizeof(rule->dst));
    offset += sizeof(rule->dst);
    memcpy(buffer + offset, &rule->sport, sizeof(rule->sport));
    offset += sizeof(rule->sport);
    memcpy(buffer + offset, &rule->dport, sizeof(rule->dport));
}

int parse_to_buffer(struct sk_buff *skb, unsigned char *buffer)
{
    struct rule *rule;

    rule = (struct rule *)kmalloc(sizeof(struct rule), GFP_KERNEL);
    if (rule == NULL)
    {
        return -1;
    }

    parse_to_rule(skb, rule);
    rule_to_buffer(rule, buffer);

    kfree(rule);

    return 0;
}

void print_rule(struct rule *rule)
{
    printk(KERN_CONT "firewall: src = %pI4", &rule->src);
    printk(KERN_CONT " dst = %pI4", &rule->dst);
    printk(KERN_CONT " sport = %d", ntohs(rule->sport));
    printk(KERN_CONT " dport = %d\n", ntohs(rule->dport));
}