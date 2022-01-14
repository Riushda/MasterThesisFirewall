#include "constant.h"
#include "utils.h"
#include "linked_list.h"

#ifndef HTABLE_H
#define HTABLE_H

typedef struct h_table
{
    linked_list_t **table;
    size_t size;
} h_table_t;

int init_table(h_table_t *h_table, size_t size);

int insert_hash(h_table_t *h_table, h_key_t *key, short rule_index);

void remove_hash(h_table_t *h_table, h_key_t *key, short rule_index);

vector_t *search_hash(h_table_t *h_table, h_key_t *key);

void destroy_table(h_table_t *h_table);

void print_table(h_table_t *h_table);

#endif