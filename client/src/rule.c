#include "rule.h"

void print_bits(size_t const size, void const *const ptr)
{
    unsigned char *b = (unsigned char *)ptr;
    unsigned char byte;
    int i, j;

    for (i = size - 1; i >= 0; i--)
    {
        for (j = 7; j >= 0; j--)
        {
            byte = (b[i] >> j) & 1;
            printf("%u", byte);
        }
    }
    puts("");
}

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