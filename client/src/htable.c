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

int init_table(h_table_t *h_table, size_t size)
{
    linked_list_t **table;
    int i;

    h_table->table = (linked_list_t **)malloc(size * sizeof(linked_list_t *));
    table = h_table->table;
    if (!table)
        return -1;

    i = 0;
    while (i < size)
    {
        table[i] = (linked_list_t *)malloc(sizeof(linked_list_t));
        if (!table[i])
            return -1;
        memset(table[i], 0, sizeof(linked_list_t));
        init_list(table[i]);
        i++;
    }

    h_table->size = size;

    return 0;
}

int insert_hash(h_table_t *h_table, unsigned char *key, int rule_index)
{
    unsigned long hashIndex;

    hashIndex = hash(key, h_table->size);
    if (insert_entry(h_table->table[hashIndex], key, rule_index))
        return -1;
    return 0;
}

void remove_hash(h_table_t *h_table, unsigned char *key, int rule_index)
{
    int i;
    unsigned long hashIndex;

    hashIndex = hash(key, h_table->size);
    for (i = 0; i < h_table->size; i++)
    {
        if (i == hashIndex)
            remove_entry(h_table->table[i], key, rule_index);
        else
            update_entry(h_table->table[i], rule_index);
    }
}

entry_t *search_hash(h_table_t *h_table, unsigned char *key)
{
    unsigned long hashIndex;

    hashIndex = hash(key, h_table->size);
    return search_entry(h_table->table[hashIndex], key);
}

void destroy_table(h_table_t *h_table)
{
    int i;

    for (i = 0; i < h_table->size; i++)
    {
        destroy_list(h_table->table[i]);
        free(h_table->table[i]);
    }

    free(h_table->table);
}

void print_table(h_table_t *h_table)
{
    int i;

    for (i = 0; i < h_table->size; i++)
    {
        if (h_table->table[i]->head != NULL)
        {
            print_list(h_table->table[i]);
            printf("----------\n");
        }
    }
}