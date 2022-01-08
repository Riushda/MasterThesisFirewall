#include <stdio.h>
#include <stdlib.h>
#include "constant.h"
#include <string.h>


#ifndef HTABLE_H
#define HTABLE_H

struct pair
{
    unsigned char key[KEY_SIZE];
    void *value;
};

struct h_table
{
    struct pair **pair_table; /* array of pairs */
    size_t c_size;            /* current size */
    size_t m_size;            /* max size */
};

struct pair *search_pair(unsigned char *key, struct h_table *h_table);

int insert_pair(unsigned char *key, void *value, struct h_table *h_table);

int remove_pair(unsigned char *key, struct h_table *h_table);

int init_table(struct h_table *h_table, size_t m_size);

int resize_table(struct h_table *h_table, short increase);

void destroy_table(struct h_table *h_table);

void display_table(struct h_table *h_table);

#endif