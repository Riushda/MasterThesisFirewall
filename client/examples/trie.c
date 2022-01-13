#include "trie.h"
#include "utils.h"
#include "rule.h"

int main()
{
    struct node *root;
    uint8_t *vector;
    int ip1;
    int ip2;
    int ip3;
    int ip4;
    int bm;
    parse_ip("0.0.0.1", &ip1, &bm);
    parse_ip("1.1", &ip2, &bm);
    parse_ip("2.2.0.1", &ip3, &bm);
    parse_ip("3.2.0.1", &ip4, &bm);
    print_bits(&ip1, 4);
    print_bits(&ip2, 4);
    print_bits(&ip3, 4);
    print_bits(&ip4, 4);

    printf("----------\n");

    root = init_node();

    insert_node(root, ip1, 3, 0);
    insert_node(root, ip2, 6, 1);
    insert_node(root, ip3, 0, 2);
    remove_node(root, ip1, 3, 0);
    print_node(root, 0);
    vector = search_node(root, ip4);
    print_bits(vector, VECTOR_SIZE);
    free_trie(root);
    free(vector);
}