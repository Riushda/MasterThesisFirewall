#include "constant.h"
#include "utils.h"

#ifndef TRIE_H
#define TRIE_H

typedef struct node
{
    vector_t vector[VECTOR_SIZE];
    struct node *children[CHILD_NBR];
    bool_t leaf;
} node_t;

typedef struct trie
{
    node_t *root;
} trie_t;

int init_trie(trie_t *trie);

node_t *init_node(void);

int insert_node(trie_t *trie, int ip, bitmask_t bitmask, short rule_index);

void remove_node(trie_t *trie, int ip, bitmask_t bitmask, short rule_index);

vector_t *search_node(trie_t *trie, int ip);

void destroy_trie(trie_t *trie);

//void print_trie(trie_t *trie, int level);

#endif