#include "linked_list.h"

void init_list(linked_list_t *list)
{
    list->head = NULL;
}

entry_t *init_entry(h_key_t *key, short rule_index)
{
    entry_t *entry;

    entry = NULL;
    entry = (entry_t *)malloc(sizeof(entry_t));

    if (entry)
    {
        memcpy(entry->key, key, KEY_SIZE);
        memset(entry->vector, 0, VECTOR_SIZE);
        set_bit_v(entry->vector, rule_index);
        entry->next = NULL;
    }

    return entry;
}

int insert_entry(linked_list_t *list, h_key_t *key, short rule_index)
{
    entry_t *current;
    entry_t *previous;

    current = list->head;
    previous = NULL;

    if (!current)
    {
        list->head = init_entry(key, rule_index);
        if (list->head)
            return 0;
        return -1;
    }

    while (current != NULL)
    {
        if (!memcmp(current->key, key, KEY_SIZE))
        {
            set_bit_v(current->vector, rule_index);
            return 0;
        }
        previous = current;
        current = current->next;
    }

    current = init_entry(key, rule_index);
    if (!current)
        return -1;
    if (previous)
    {
        previous->next = current;
    }
    return 0;
}

void update_entry(linked_list_t *list, short rule_index)
{
    entry_t *current;
    current = list->head;

    while (current != NULL)
    {
        unset_shift_v(current->vector, rule_index);
        current = current->next;
    }
}

void remove_entry(linked_list_t *list, h_key_t *key, short rule_index)
{
    entry_t *current;
    entry_t *previous;

    current = list->head;
    previous = NULL;

    while (current != NULL)
    {
        if (!memcmp(current->key, key, KEY_SIZE))
        {
            unset_shift_v(current->vector, rule_index);
            if (is_null_v(current->vector))
            {
                if (previous)
                {
                    previous->next = current->next;
                    free(current);
                    current = previous->next;
                }
                else
                {
                    list->head = current->next;
                    free(current);
                    current = list->head;
                }
                continue;
            }
        }
        else
        {
            unset_shift_v(current->vector, rule_index);
        }

        previous = current;
        current = current->next;
    }
}

entry_t *search_entry(linked_list_t *list, h_key_t *key)
{
    entry_t *current;

    current = list->head;

    while (current != NULL)
    {
        if (!memcmp(current->key, key, KEY_SIZE))
        {
            return current;
        }
        current = current->next;
    }

    return NULL;
}

void destroy_list(linked_list_t *list)
{
    entry_t *current;
    entry_t *next;

    current = list->head;
    next = NULL;

    while (current != NULL)
    {
        next = current->next;
        free(current);
        current = next;
    }
}

void print_list(linked_list_t *list)
{
    entry_t *current;
    char buf[KEY_SIZE + 1];

    current = list->head;
    memset(buf, 0, KEY_SIZE);

    while (current != NULL)
    {
        memcpy(buf, current->key, KEY_SIZE);
        buf[KEY_SIZE] = '\0';
        printf("%s:", buf);
        print_bits(current->vector, VECTOR_SIZE);
        current = current->next;
    }
}