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
    node = (node_t *)kmalloc(sizeof(node_t), GFP_KERNEL);

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
    node_t *element;

    element = trie->root;

    for (level = 0; level < bitmask; level++)
    {
        index = is_set_ip(ip, level);

        if (!element->children[index])
        {
            element->children[index] = init_node();
            if (!element->children[index])
                return -1;
            memcpy(element->children[index]->vector, element->vector, VECTOR_SIZE);
        }

        element = element->children[index];
    }

    element->leaf = 1;

    update_vector(element, rule_index, set_bit_v);

    return 0;
}

void remove_node(trie_t *trie, int ip, bitmask_t bitmask, short rule_index)
{
    int level;
    int index;
    node_t *element;

    element = trie->root;
    for (level = 0; level < bitmask; level++)
    {
        index = is_set_ip(ip, level);

        if (!element->children[index])
            element->children[index] = init_node();

        element = element->children[index];
    }

    update_vector(trie->root, rule_index, unset_shift_v);
}

vector_t *search_node(trie_t *trie, int ip)
{
    int level;
    int index;
    node_t *element;
    vector_t *vector;

    vector = NULL;
    element = trie->root;

    for (level = 0; level < IP_SIZE; level++)
    {
        vector = element->vector;
        index = is_set_ip(ip, level);
        if (!element->children[index])
            return vector;
        element = element->children[index];
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

    kfree(node);
}

void destroy_trie(trie_t *trie)
{
    destroy_node(trie->root);
}

void print_node(node_t *node, int level)
{
    int i;

    printk(KERN_INFO "Vector: ");
    print_bits(node->vector, VECTOR_SIZE);

    for (i = 0; i < CHILD_NBR; i++)
    {
        printk(KERN_INFO "Has child %d: %d\n", i, node->children[i] != NULL);
    }

    printk(KERN_INFO "Leaf: %d\n", node->leaf);
    printk(KERN_INFO "Level: %d\n", level);
    printk(KERN_INFO "----------\n");

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