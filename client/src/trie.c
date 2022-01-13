#include "trie.h"

struct node *init_node(void)
{
    struct node *node;
    int i;

    node = NULL;
    node = (struct node *)malloc(sizeof(struct node));

    if (node)
    {
        i = 0;
        memset(node->vector, 0, VECTOR_SIZE);
        node->leaf = 0;

        for (i = 0; i < CHILD_NBR; i++)
            node->children[i] = NULL;
    }

    return node;
}

void update_vector(struct node *node, int rule_index, void (*update)(void *, int))
{
    int i;

    update(node->vector, rule_index);

    for (i = 0; i < CHILD_NBR; i++)
    {
        if (node->children[i])
        {
            update_vector(node->children[i], rule_index, update);
        }
    }
}

void insert_node(struct node *root, const int ip, int bitmask, int rule_index)
{
    int level;
    int index;
    struct node *current;

    current = root;

    for (level = 0; level < bitmask; level++)
    {
        index = is_set_ip(ip, level);

        if (!current->children[index])
        {
            current->children[index] = init_node();
            memcpy(current->children[index]->vector, current->vector, VECTOR_SIZE);
        }

        current = current->children[index];
    }

    current->leaf = 1;

    update_vector(current, rule_index, set_bit_v);
}

void remove_node(struct node *root, const int ip, int bitmask, int rule_index)
{
    int level;
    int index;
    struct node *current;

    current = root;
    for (level = 0; level < bitmask; level++)
    {
        index = is_set_ip(ip, level);

        if (!current->children[index])
            current->children[index] = init_node();

        current = current->children[index];
    }

    update_vector(root, rule_index, unset_shift_v);
}

uint8_t *search_node(struct node *root, int ip)
{
    int level;
    int index;
    struct node *current;
    uint8_t *vector;

    current = root;
    vector = (uint8_t *)malloc(VECTOR_SIZE);
    if (vector == NULL)
    {
        return NULL;
    }

    memset(vector, 0, VECTOR_SIZE);

    for (level = 0; level < IP_SIZE; level++)
    {
        index = is_set_ip(ip, level);
        vector = memcpy(vector, current->vector, VECTOR_SIZE);
        if (!current->children[index])
            return vector;
        current = current->children[index];
    }

    return vector;
}

void free_trie(struct node *node)
{
    int i;

    for (i = 0; i < CHILD_NBR; i++)
    {
        if (node->children[i])
        {
            free_trie(node->children[i]);
        }
    }

    free(node);
}

void print_node(struct node *node, int level)
{
    int i;

    printf("Vector: ");
    print_bits(node->vector, VECTOR_SIZE);

    for (i = 0; i < CHILD_NBR; i++)
    {
        printf("Has child %d: %d\n", i, node->children[i] != NULL);
    }

    printf("Leaf: %d\n", node->leaf);
    printf("Level: %d\n", level);
    printf("----------\n");

    for (i = 0; i < CHILD_NBR; i++)
    {
        if (node->children[i])
        {
            print_node(node->children[i], level + 1);
        }
    }
}