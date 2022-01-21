#include "linked_list.h"

void init_list(linked_list_t *list)
{
    list->head = NULL;
}

entry_t *init_entry(h_key_t *key, short rule_index)
{
    entry_t *entry;

    entry = NULL;
    entry = (entry_t *)kmalloc(sizeof(entry_t), GFP_KERNEL);

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
    entry_t *element;
    entry_t *previous;

    element = list->head;
    previous = NULL;

    if (!element)
    {
        list->head = init_entry(key, rule_index);
        if (list->head)
            return 0;
        return -1;
    }

    while (element != NULL)
    {
        if (!memcmp(element->key, key, KEY_SIZE))
        {
            set_bit_v(element->vector, rule_index);
            return 0;
        }
        previous = element;
        element = element->next;
    }

    element = init_entry(key, rule_index);
    if (!element)
        return -1;
    if (previous)
    {
        previous->next = element;
    }
    return 0;
}

void update_entry(linked_list_t *list, short rule_index)
{
    entry_t *element;
    element = list->head;

    while (element != NULL)
    {
        unset_shift_v(element->vector, rule_index);
        element = element->next;
    }
}

void remove_entry(linked_list_t *list, h_key_t *key, short rule_index)
{
    entry_t *element;
    entry_t *previous;

    element = list->head;
    previous = NULL;

    while (element != NULL)
    {
        if (!memcmp(element->key, key, KEY_SIZE))
        {
            unset_shift_v(element->vector, rule_index);
            if (is_null_v(element->vector))
            {
                if (previous)
                {
                    previous->next = element->next;
                    kfree(element);
                    element = previous->next;
                }
                else
                {
                    list->head = element->next;
                    kfree(element);
                    element = list->head;
                }
                continue;
            }
        }
        else
        {
            unset_shift_v(element->vector, rule_index);
        }

        previous = element;
        element = element->next;
    }
}

entry_t *search_entry(linked_list_t *list, h_key_t *key)
{
    entry_t *element;

    element = list->head;

    while (element != NULL)
    {
        if (!memcmp(element->key, key, KEY_SIZE))
        {
            return element;
        }
        element = element->next;
    }

    return NULL;
}

void destroy_list(linked_list_t *list)
{
    entry_t *element;
    entry_t *next;

    element = list->head;
    next = NULL;

    while (element != NULL)
    {
        next = element->next;
        kfree(element);
        element = next;
    }
}

/*void print_list(linked_list_t *list)
{
    entry_t *element;
    char buf[KEY_SIZE + 1];

    element = list->head;
    memset(buf, 0, KEY_SIZE);

    while (element != NULL)
    {
        memcpy(buf, element->key, KEY_SIZE);
        buf[KEY_SIZE] = '\0';
        printf("%s:", buf);
        print_bits(element->vector, VECTOR_SIZE);
        element = element->next;
    }
}*/