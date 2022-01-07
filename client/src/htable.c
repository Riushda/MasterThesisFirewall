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
        resize_table(h_table, 1);

    table = h_table->pair_table;

    pair = (struct pair *)malloc(sizeof(struct pair));
    if (pair == NULL)
    {
        return -1;
    }

    memset(pair->key, 0, sizeof(pair->key));
    memcpy(pair->key, key, sizeof(pair->key));

    pair->value = value;

    hashIndex = hash(key, h_table->m_size);

    while (table[hashIndex] != NULL)
    {
        ++hashIndex;
        hashIndex %= h_table->m_size;
    }

    table[hashIndex] = pair;
    h_table->c_size++;

    return 0;
}

void remove_pair(unsigned char *key, struct h_table *h_table)
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
        resize_table(h_table, 0);
}

void init_table(struct h_table *h_table, size_t m_size)
{
    struct pair **table;
    int i;

    h_table->pair_table = (struct pair **)malloc(m_size * sizeof(struct pair *));
    table = h_table->pair_table;
    i = 0;

    while (i < m_size)
    {
        memset(&table[i], 0, sizeof(struct pair *));
        i++;
    }

    memset(&h_table->c_size, 0, sizeof(size_t));
    memset(&h_table->m_size, 0, sizeof(size_t));
    memcpy(&h_table->m_size, &m_size, sizeof(size_t));
}

void resize_table(struct h_table *h_table, short increase)
{
    struct pair **table;
    size_t new_size;
    size_t old_size;
    int i;

    memcpy(&old_size, &h_table->m_size, sizeof(size_t));
    if (increase)
        h_table->m_size = h_table->m_size * 2;
    else
    {
        if (h_table->m_size <= 1)
        {
            return;
        }
        h_table->m_size = h_table->m_size / 2;
    }
    table = h_table->pair_table;
    h_table->pair_table = (struct pair **)malloc(h_table->m_size * sizeof(struct pair *));
    i = 0;

    while (i < h_table->m_size)
    {
        memset(&h_table->pair_table[i], 0, sizeof(struct pair *));
        i++;
    }

    memset(&h_table->c_size, 0, sizeof(size_t));

    i = 0;

    while (i < old_size)
    {
        if (table[i] != NULL)
        {
            insert_pair(table[i]->key, table[i]->value, h_table);
            free(table[i]);
        }
        i++;
    }
    free(table);
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

void display(struct h_table *h_table)
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