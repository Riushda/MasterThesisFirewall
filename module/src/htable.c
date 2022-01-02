#include "htable.h"

unsigned long hash(unsigned char *str, size_t size)
{
    unsigned long hash;
    int c;

    hash = 5381;
    while ((c = *str++))
        hash = ((hash << 5) + hash) + c;
        
    return hash % size;
}

struct item *search_item(unsigned char *key, struct item *table[], size_t size)
{
    unsigned long hashIndex;

    hashIndex = hash(key, size);
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
    struct item *item;
    unsigned long hashIndex;

    item = (struct item *)kmalloc(sizeof(struct item), GFP_KERNEL);
    if (item == NULL)
    {
        return -1;
    }

    memset(item->key, 0, sizeof(item->key));
    memcpy(item->key, key, sizeof(item->key));

    hashIndex = hash(key, size);

    while (table[hashIndex] != NULL)
    {
        ++hashIndex;
        hashIndex %= size;
    }

    table[hashIndex] = item;

    return 0;
}

void free_item(unsigned char *key, struct item *table[], size_t size)
{
    unsigned long hashIndex;

    hashIndex = hash(key, size);
    while (table[hashIndex] != NULL)
    {
        if (!memcmp(table[hashIndex]->key, key, sizeof(table[hashIndex]->key)))
        {
            kfree(table[hashIndex]);
            table[hashIndex] = NULL;
        }
        ++hashIndex;
        hashIndex %= size;
    }
}

void free_table(struct item *table[], size_t size)
{
    int i;

    i = 0;
    while (i < size)
    {
        if (table[i] != NULL)
        {
            kfree(table[i]);
        }
        i++;
    }
}