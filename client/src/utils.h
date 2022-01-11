#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "constant.h"

#ifndef UTILS_H
#define UTILS_H

int count_args(char *line);

void arg_lengths(char *line, int argc, int *lengths);

void arg_values(char *line, int argc, int *lengths, char **argv);

void print_bits(void const *const ptr, size_t const size);

int bitmask(size_t size);

int is_set_ip(int ip, short offset);

int is_set_v(void *ptr, int index);

void set_bit_v(void *ptr, int index);

void unset_shift_v(void *ptr, int index);

#endif
