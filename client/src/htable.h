#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#ifndef HTABLE_H
#define HTABLE_H

#define KEY_SIZE 5

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

unsigned long hash(unsigned char *str, size_t size);

struct pair *search_pair(unsigned char *key, struct h_table *h_table);

int insert_pair(unsigned char *key, void *value, struct h_table *h_table);

void remove_pair(unsigned char *key, struct h_table *h_table);

void init_table(struct h_table *h_table, size_t m_size);

void resize_table(struct h_table *h_table, short increase);

void destroy_table(struct h_table *h_table);

void display(struct h_table *h_table);

#endif