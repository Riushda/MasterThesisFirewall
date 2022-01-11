#include <stdio.h>
#include <stdlib.h>
#include "utils.h"
#include "constant.h"

#ifndef TRIE_H
#define TRIE_H

struct node *init_node(void);

void update_vector(struct node *node, int rule_index, void (*update)(void *, int));

void insert_node(struct node *root, const int ip, int bitmask, int rule_index);

uint8_t *search_node(struct node *root, int ip);

void remove_node(struct node *root, const int ip, int bitmask, int rule_index);

void free_trie(struct node *node);

void print_node(struct node *node, int level);

#endif