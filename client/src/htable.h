#include <stdio.h>
#include <string.h>
#include <stdlib.h>

struct item
{
    unsigned char key[12];
};


struct item *search_item(unsigned char *key, struct item *table[], size_t size);

int insert_item(unsigned char *key, struct item *table[], size_t size);

void delete_item(unsigned char *key, struct item *table[], size_t size);

void display_table(struct item *table[], size_t size);

void free_table(struct item *table[], size_t size);