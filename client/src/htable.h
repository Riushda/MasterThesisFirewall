#include "utils.h"
#include "constant.h"
#include "linked_list.h"

#ifndef HTABLE_H
#define HTABLE_H

typedef struct h_table
{
    linked_list_t **table;
    size_t size;
} h_table_t;

int init_table(h_table_t *h_table, size_t size);

int insert_hash(h_table_t *h_table, unsigned char *key, int rule_index);

void remove_hash(h_table_t *h_table, unsigned char *key, int rule_index);

entry_t *search_hash(h_table_t *h_table, unsigned char *key);

void destroy_table(h_table_t *h_table);

void print_table(h_table_t *h_table);

#endif