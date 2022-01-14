#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "constant.h"

#ifndef UTILS_H
#define UTILS_H

int count_args(string_t *line);

void arg_lengths(string_t *line, int argc, int *lengths);

void arg_values(string_t *line, int argc, int *lengths, char **argv);

void print_bits(void const *const ptr, size_t const size);

#endif
