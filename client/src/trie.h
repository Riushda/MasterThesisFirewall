#include "utils.h"
#include "constant.h"

#ifndef TRIE_H
#define TRIE_H

typedef struct node
{
    uint8_t vector[VECTOR_SIZE];
    struct node *children[CHILD_NBR];
    uint8_t leaf;
} node_t;

struct node *init_node(void);

void insert_node(struct node *root, const int ip, int bitmask, int rule_index);

uint8_t *search_node(struct node *root, int ip);

void remove_node(struct node *root, const int ip, int bitmask, int rule_index);

void free_trie(struct node *node);

void print_node(struct node *node, int level);

#endif