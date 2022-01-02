#include <linux/ip.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

struct rule
{
    __be32 src;
    __be32 dst;
    __be16 sport;
    __be16 dport;
};

void print_bits(size_t const size, void const *const ptr);

int bitmask(size_t size, int *bitmask);

int parse_ip(unsigned char *str_ip, __be32 *ip);

int parse_port(unsigned char *str_port, __be16 *port);

