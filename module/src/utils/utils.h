#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/netlink.h>
#include <linux/skbuff.h>
#include <linux/netfilter.h>
#include <linux/netfilter_ipv4.h>
#include <linux/ip.h>
#include <linux/tcp.h>
#include <linux/udp.h>
#include <linux/inet.h>
#include <linux/slab.h>
#include <linux/string.h>

#include "constant.h"

#ifndef UTILS_H
#define UTILS_H

void print_bits(void const *const ptr, size_t const size);

bool_t is_set_ip(int ip, short offset);

bool_t is_set_v(vector_t *vector, short index);

void set_bit_v(vector_t *vector, short index);

void unset_bit_v(vector_t *vector, short index);

void unset_shift_v(vector_t *vector, short index);

bool_t is_null_v(vector_t *vector);

short first_match_index(vector_t *vector);

vector_t *and_v(vector_t *vector1, vector_t *vector2);

vector_t *or_v(vector_t *vector1, vector_t *vector2);

#endif
