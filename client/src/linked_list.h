#include "constant.h"
#include "utils.h"

typedef struct entry
{
    unsigned char key[KEY_SIZE];
    uint8_t vector[VECTOR_SIZE];
    struct entry *next;
} entry_t;

typedef struct linked_list
{
    entry_t *head;
} linked_list_t;

void init_list(linked_list_t *list);

entry_t *init_entry(unsigned char *key, int rule_index);

int insert_entry(linked_list_t *list, unsigned char *key, int rule_index);

void update_entry(linked_list_t *list, int rule_index);

void remove_entry(linked_list_t *list, unsigned char *key, int rule_index);

entry_t *search_entry(linked_list_t *list, unsigned char *key);

void destroy_list(linked_list_t *list);

void print_list(linked_list_t *list);