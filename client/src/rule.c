#include "rule.h"

int bitmask(size_t size, int *bitmask)
{
    int i;

    if (size > 32)
        return -1;

    memset(bitmask, 0, sizeof(int));

    for (i = 0; i < size; i++)
        *bitmask = (*bitmask << 1) + 1;

    return 0;
}

int parse_not(unsigned char *str_not, uint8_t *not_v)
{
    memset(not_v, 0, sizeof(uint8_t));

    if (!memcmp(str_not, "!", 1))
    {
        *not_v = 1;
        return 1;
    }
    else
    {
        *not_v = 0;
        return 0;
    }
}

int parse_ip(unsigned char *str_ip, __be32 *ip, uint8_t *not_v)
{

    struct in_addr addr;
    char *str;

    memset(ip, 0, sizeof(__be32));
    str = str_ip;

    if (parse_not(str, not_v))
    {
        str++;
    }

    if (strlen(str_ip) < 7)
    { /* 7 is the minimum valid length for an IP */
        if (!memcmp(str, "*", 1))
        {
            memcpy(ip, "*", 1);
            return 0;
        }
        else
        {
            return -1;
        }
    }

    if (!inet_aton(str, &addr))
    {
        return -1;
    }

    memcpy(ip, &addr, sizeof(addr));

    return 0;
}

void parse_port(unsigned char *str_port, __be16 *port, uint8_t *not_v)
{
    uint16_t hport;
    char *str;

    str = str_port;
    memset(port, 0, sizeof(__be16));

    if (parse_not(str, not_v))
    {
        str++;
    }

    if (!memcmp(str, "*", 1))
    {
        memcpy(port, "*", 1);
        return;
    }

    hport = htons(atoi(str));

    memcpy(port, &hport, sizeof(hport));
}

void print_rule(struct rule rule)
{
    struct in_addr addr;

    if (rule.not_src)
    {
        printf("!");
    }

    memcpy(&addr, &rule.src, sizeof(addr));
    printf("Src: %s\n", inet_ntoa(addr));

    if (rule.not_dst)
    {
        printf("!");
    }

    memcpy(&addr, &rule.dst, sizeof(addr));
    printf("Dst: %s\n", inet_ntoa(addr));

    if (rule.not_sport)
    {
        printf("!");
    }

    printf("Sport: %d\n", ntohs(rule.sport));

    if (rule.not_dport)
    {
        printf("!");
    }

    printf("Dport: %d\n", ntohs(rule.dport));
}