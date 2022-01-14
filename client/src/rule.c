#include "rule.h"

int parse_not(string_t *str_not, bool_t *not_v)
{
    memset(not_v, 0, sizeof(bool_t));

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

int parse_ip(string_t *str_ip, int *ip, bitmask_t *bitmask)
{
    struct in_addr addr;
    char str[strlen(str_ip)];
    char *token;
    const char delimiter[2] = "/";

    memset(ip, 0, sizeof(int));
    strcpy(str, str_ip);

    if (strlen(str_ip) == 1) /* 7 is the minimum valid length for an IP */
    {
        if (!memcmp(str, "*", 1))
        {
            memset(ip, 0, sizeof(int));
            return 0;
        }
        else
        {
            return -1;
        }
    }

    token = strtok(str, delimiter);
    if (token)
    {
        if (!inet_aton(token, &addr))
        {
            return -1;
        }
    }

    memcpy(ip, &addr, sizeof(struct in_addr));
    *ip = htonl(*ip);

    token = strtok(NULL, delimiter);
    if (token)
    {
        *bitmask = atoi(token);
        if (!*bitmask)
            return -1;
    }
    else
    {
        *bitmask = 32;
    }

    return 0;
}

void parse_port(string_t *str_port, short *port, bool_t *not_v)
{
    short hport;
    char *str;

    str = str_port;
    memset(port, 0, sizeof(short));

    if (parse_not(str, not_v))
    {
        str++;
    }

    if (!memcmp(str, "*", 1))
    {
        memset(port, 0, sizeof(short));
        return;
    }

    hport = htons(atoi(str));

    memcpy(port, &hport, sizeof(short));
}

void print_rule(rule_t rule)
{
    struct in_addr addr;
    int src;
    int dst;

    if (rule.not_src)
    {
        printf("!");
    }

    src = ntohl(rule.src);
    memcpy(&addr, &src, sizeof(struct in_addr));
    printf("Src: %s/%d\n", inet_ntoa(addr), rule.src_bm);

    if (rule.not_dst)
    {
        printf("!");
    }

    dst = ntohl(rule.dst);
    memcpy(&addr, &dst, sizeof(struct in_addr));
    printf("Dst: %s/%d\n", inet_ntoa(addr), rule.dst_bm);

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
