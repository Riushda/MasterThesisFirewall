#include "htable.h"

unsigned long hash(unsigned char *str, size_t size)
{
    unsigned long hash = 5381;
    int c;

    while (c = *str++)
        hash = ((hash << 5) + hash) + c;

    return hash % size;
}

struct item *search_item(unsigned char *key, struct item *table[], size_t size)
{
    unsigned long hashIndex = hash(key, size);

    while (table[hashIndex] != NULL)
    {

        if (!memcmp(table[hashIndex]->key, key, sizeof(table[hashIndex]->key)))
            return table[hashIndex];

        ++hashIndex;
        hashIndex %= size;
    }

    return NULL;
}

int insert_item(unsigned char *key, struct item *table[], size_t size)
{
    struct item *item = (struct item *)malloc(sizeof(struct item));
    if (item == NULL)
    {
        return -1;
    }
    
    memset(item->key, 0, sizeof(item->key));
    memcpy(item->key, key, sizeof(item->key));

    unsigned long hashIndex = hash(key, size);

    while (table[hashIndex] != NULL)
    {
        ++hashIndex;
        hashIndex %= size;
    }

    table[hashIndex] = item;
}

void delete_item(unsigned char *key, struct item *table[], size_t size)
{
    unsigned long hashIndex = hash(key, size);

    while (table[hashIndex] != NULL)
    {
        if (!memcmp(table[hashIndex]->key, key, sizeof(table[hashIndex]->key)))
        {
            free(table[hashIndex]);
            table[hashIndex] = NULL;
        }
        ++hashIndex;
        hashIndex %= size;
    }
}

void display_table(struct item *table[], size_t size)
{
    int i = 0;

    for (i = 0; i < size; i++)
    {

        if (table[i] != NULL)
            printf(" (%s)", table[i]->key);
        else
            printf(" ~~ ");
    }

    printf("\n");
}

void free_table(struct item *table[], size_t size)
{
    int i = 0;

    while (i < size)
    {
        if (table[i] != NULL)
        {
            free(table[i]);
        }
        i++;
    }
}