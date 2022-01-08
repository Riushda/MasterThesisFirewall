#include <linux/slab.h>
#include "constant.h"

#ifndef HTABLE_H
#define HTABLE_H

struct item
{
    unsigned char key[RULE_SIZE];
};

unsigned long hash(unsigned char *str, size_t size);

struct item *search_item(unsigned char *key, struct item *table[], size_t size);

int insert_item(unsigned char *key, struct item *table[], size_t size);

void free_item(unsigned char *key, struct item *table[], size_t size);

void free_table(struct item *table[], size_t size);

#endif