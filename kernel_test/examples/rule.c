#include "rule.h"

int main()
{
    rule_t rule;
    trie_t src_trie;
    trie_t dst_trie;
    h_table_t sport_table;
    h_table_t dport_table;

    memset(&rule, 0, sizeof(rule_t));

    parse_ip("127.0.0.1/24", &rule.src, &rule.src_bm);
    parse_ip("127.0.0.1/24", &rule.dst, &rule.dst_bm);
    parse_port("22", &rule.sport, &rule.not_sport);
    parse_port("22", &rule.dport, &rule.not_dport);
    rule.index = 0;

    print_rule(rule);

    init_rules(&src_trie, &dst_trie, &sport_table, &dport_table);

    insert_rule(&src_trie, &dst_trie, &sport_table, &dport_table, &rule);

    print_table(&sport_table);
    print_table(&dport_table);

    destroy_rules(&src_trie, &dst_trie, &sport_table, &dport_table);
    return 0;
}