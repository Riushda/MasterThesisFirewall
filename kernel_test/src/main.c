#include "rule.h"

int main()
{
    rule_t rule;
    rule_struct_t rule_struct;
    memset(&rule_struct, 0, sizeof(rule_struct_t));
    memset(&rule, 0, sizeof(rule_t));

    parse_ip("127.0.0.1/24", &rule.src, &rule.src_bm);
    parse_ip("127.0.0.1/24", &rule.dst, &rule.dst_bm);
    parse_port("22", &rule.sport, &rule.not_sport);
    parse_port("22", &rule.dport, &rule.not_dport);
    rule.index = 2;
    rule.action = 1;

    print_rule(rule);

    init_rules(&rule_struct);

    insert_rule(&rule_struct, rule);
    //remove_rule(&rule_struct, rule);

    rule.dport = ntohs(23);

    /*print_trie(rule_struct.src_trie, 0);
    print_table(rule_struct.sport_table);
    print_table(rule_struct.dport_table);*/

    printf("%d\n", match_rule(&rule_struct, rule));

    destroy_rules(&rule_struct);

    vector_t vector[VECTOR_SIZE];
    memset(vector, 0, VECTOR_SIZE);
    //print_bits(vector, VECTOR_SIZE);
    return 0;
}