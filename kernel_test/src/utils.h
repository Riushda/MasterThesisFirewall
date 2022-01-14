#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "constant.h"

#ifndef UTILS_H
#define UTILS_H

void print_bits(void const *const ptr, size_t const size);

int is_set_ip(int ip, short offset);

int is_set_v(vector_t *vector, short index);

void set_bit_v(vector_t *vector, short index);

void unset_shift_v(vector_t *vector, short index);

int is_null_v(vector_t *vector);

int first_match_index(vector_t *vector);

vector_t *and_v(vector_t *vector1, vector_t *vector2);

vector_t *or_v(vector_t *vector1, vector_t *vector2);

#endif
