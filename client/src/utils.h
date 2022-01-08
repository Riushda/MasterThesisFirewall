#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef UTILS_H
#define UTILS_H

void print_bits(void const *const ptr, size_t const size);

int count_args(char *line);

void arg_lengths(char *line, int argc, int *lengths);

void arg_values(char *line, int argc, int *lengths, char **argv);

#endif
