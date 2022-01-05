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

int parse_ip(unsigned char *str_ip, __be32 *ip)
{
    struct in_addr addr;
    int err;

    err = inet_aton(str_ip, &addr);
    if (!err)
    {
        return -1;
    }

    memset(ip, 0, sizeof(__be32));
    memcpy(ip, &addr, sizeof(addr));

    return 0;
}

int parse_port(unsigned char *str_port, __be16 *port)
{
    uint16_t hport;

    hport = htons(atoi(str_port));

    memset(port, 0, sizeof(__be16));
    memcpy(port, &hport, sizeof(hport));

    return 0;
}