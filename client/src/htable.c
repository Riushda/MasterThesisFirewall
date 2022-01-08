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

struct pair *search_pair(unsigned char *key, struct h_table *h_table)
{
    unsigned long hashIndex;
    struct pair **table;

    hashIndex = hash(key, h_table->m_size);
    table = h_table->pair_table;

    while (table[hashIndex] != NULL)
    {
        if (!memcmp(table[hashIndex]->key, key, sizeof(table[hashIndex]->key)))
            return table[hashIndex];

        ++hashIndex;
        hashIndex %= h_table->m_size;
    }

    return NULL;
}

int insert_pair(unsigned char *key, void *value, struct h_table *h_table)
{
    struct pair *pair;
    unsigned long hashIndex;
    struct pair **table;

    if (h_table->c_size >= h_table->m_size / 2)
        if (resize_table(h_table, 1))
        {
            return -1;
        }

    pair = (struct pair *)malloc(sizeof(struct pair));
    if (pair == NULL)
    {
        return -1;
    }

    memset(pair->key, 0, sizeof(pair->key));
    memcpy(pair->key, key, sizeof(pair->key));
    pair->value = value;
    hashIndex = hash(key, h_table->m_size);
    table = h_table->pair_table;

    while (table[hashIndex] != NULL)
    {
        ++hashIndex;
        hashIndex %= h_table->m_size;
    }

    table[hashIndex] = pair;
    h_table->c_size++;
    return 0;
}

int remove_pair(unsigned char *key, struct h_table *h_table)
{
    unsigned long hashIndex;
    struct pair **table;

    table = h_table->pair_table;

    hashIndex = hash(key, h_table->m_size);
    while (table[hashIndex] != NULL)
    {
        if (!memcmp(table[hashIndex]->key, key, sizeof(table[hashIndex]->key)))
        {

            free(table[hashIndex]);
            table[hashIndex] = NULL;
            h_table->c_size--;
        }
        ++hashIndex;
        hashIndex %= h_table->m_size;
    }

    if (h_table->c_size <= h_table->m_size / 4)
        if (resize_table(h_table, 0))
        {
            return -1;
        }
}

int init_table(struct h_table *h_table, size_t m_size)
{
    struct pair **table;
    int i;

    h_table->pair_table = (struct pair **)malloc(m_size * sizeof(struct pair *));
    table = h_table->pair_table;
    if (table == NULL)
    {
        return -1;
    }

    i = 0;

    while (i < m_size)
    {
        memset(&table[i], 0, sizeof(struct pair *));
        i++;
    }

    memset(&h_table->c_size, 0, sizeof(size_t));
    h_table->m_size = m_size;
}

int resize_table(struct h_table *h_table, short increase)
{
    struct pair **new_table;
    struct pair **old_table;
    size_t new_size;
    size_t old_size;
    unsigned long hashIndex;
    int i;

    old_size = h_table->m_size;
    new_size = old_size;

    if (increase)
        new_size = new_size * 2;
    else
    {
        if (old_size <= 1)
        {
            return -1;
        }
        new_size = new_size / 2;
    }

    h_table->m_size = new_size;
    old_table = h_table->pair_table;

    h_table->pair_table = (struct pair **)malloc(h_table->m_size * sizeof(struct pair *));
    new_table = h_table->pair_table;

    if (new_table == NULL)
    {
        return -1;
    }

    memset(&h_table->c_size, 0, sizeof(size_t));
    i = 0;

    while (i < new_size)
    {
        memset(&new_table[i], 0, sizeof(struct pair *));
        i++;
    }

    i = 0;

    while (i < old_size)
    {
        if (old_table[i] != NULL)
        {
            hashIndex = hash(old_table[i]->key, new_size);
            while (new_table[hashIndex] != NULL)
            {
                ++hashIndex;
                hashIndex %= new_size;
            }
            new_table[hashIndex] = old_table[i];
            h_table->c_size++;
        }
        i++;
    }

    free(old_table);
    return 0;
}

void destroy_table(struct h_table *h_table)
{
    int i;
    struct pair **table;

    table = h_table->pair_table;

    i = 0;
    while (i < h_table->m_size)
    {
        if (table[i] != NULL)
        {
            free(table[i]);
        }
        i++;
    }

    free(table);
}

void display_table(struct h_table *h_table)
{
    int i = 0;
    struct pair **table;

    table = h_table->pair_table;

    for (i = 0; i < h_table->m_size; i++)
    {

        if (table[i] != NULL)
        {
            printf(" (%s,%d)", table[i]->key, table[i]->value);
        }

        else
            printf(" ~~ ");
    }

    printf("\n");
}