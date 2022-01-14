#include "trie.h"

int init_trie(trie_t *trie)
{
    trie->root = init_node();
    if (!trie->root)
        return -1;
    return 0;
}

node_t *init_node(void)
{
    node_t *node;
    int i;

    node = NULL;
    node = (node_t *)malloc(sizeof(node_t));

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

void update_vector(node_t *node, short rule_index, void (*update)(vector_t *, short))
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

int insert_node(trie_t *trie, int ip, bitmask_t bitmask, short rule_index)
{
    int level;
    int index;
    node_t *current;

    current = trie->root;

    for (level = 0; level < bitmask; level++)
    {
        index = is_set_ip(ip, level);

        if (!current->children[index])
        {
            current->children[index] = init_node();
            if (!current->children[index])
                return -1;
            memcpy(current->children[index]->vector, current->vector, VECTOR_SIZE);
        }

        current = current->children[index];
    }

    current->leaf = 1;

    update_vector(current, rule_index, set_bit_v);

    return 0;
}

void remove_node(trie_t *trie, int ip, bitmask_t bitmask, short rule_index)
{
    int level;
    int index;
    node_t *current;

    current = trie->root;
    for (level = 0; level < bitmask; level++)
    {
        index = is_set_ip(ip, level);

        if (!current->children[index])
            current->children[index] = init_node();

        current = current->children[index];
    }

    update_vector(trie->root, rule_index, unset_shift_v);
}

vector_t *search_node(trie_t *trie, int ip)
{
    int level;
    int index;
    node_t *current;
    vector_t *vector;

    vector = NULL;
    current = trie->root;

    for (level = 0; level < IP_SIZE; level++)
    {
        vector = current->vector;
        index = is_set_ip(ip, level);
        if (!current->children[index])
            return vector;
        current = current->children[index];
    }

    return vector;
}

void destroy_node(node_t *node)
{
    int i;

    for (i = 0; i < CHILD_NBR; i++)
    {
        if (node->children[i])
        {
            destroy_node(node->children[i]);
        }
    }

    free(node);
}

void destroy_trie(trie_t *trie)
{
    destroy_node(trie->root);
}

void print_node(node_t *node, int level)
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

void print_trie(trie_t *trie, int level)
{
    print_node(trie->root, level);
}