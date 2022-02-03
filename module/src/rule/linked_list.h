#include "../utils/constant.h"
#include "../utils/utils.h"

typedef struct entry
{
    h_key_t key[KEY_SIZE];
    vector_t vector[VECTOR_SIZE];
    struct entry *next;
} entry_t;

typedef struct linked_list
{
    entry_t *head;
} linked_list_t;

void init_list(linked_list_t *list);

entry_t *init_entry(h_key_t *key, short rule_index);

int insert_entry(linked_list_t *list, h_key_t *key, short rule_index);

void update_entry(linked_list_t *list, short rule_index);

void remove_entry(linked_list_t *list, h_key_t *key, short rule_index);

entry_t *search_entry(linked_list_t *list, h_key_t *key);

void destroy_list(linked_list_t *list);

void print_list(linked_list_t *list);