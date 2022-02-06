#include "rule.h"
#include "data_constraint.h"

int main()
{
    rule_t rule;
    rule_struct_t rule_struct;
    memset(&rule_struct, 0, sizeof(rule_struct_t));
    memset(&rule, 0, sizeof(rule_t));

    parse_ip("127.0.0.1/24", &rule.src, &rule.src_bm);
    parse_ip("127.0.0.1/24", &rule.dst, &rule.dst_bm);
    parse_port("*", &rule.sport, &rule.not_sport);
    parse_port("22", &rule.dport, &rule.not_dport);
    rule.index = 2;
    rule.action = 1;

    //print_rule(rule);

    init_rules(&rule_struct);

    insert_rule(&rule_struct, rule);
    //remove_rule(&rule_struct, rule);

    //rule.dport = ntohs(23);

    rule_t rule2;
    memset(&rule2, 0, sizeof(rule_t));

    parse_ip("127.0.0.1/24", &rule2.src, &rule2.src_bm);
    parse_ip("127.0.0.1/24", &rule2.dst, &rule2.dst_bm);
    parse_port("22", &rule2.sport, &rule2.not_sport);
    parse_port("22", &rule2.dport, &rule2.not_dport);

    /*print_trie(rule_struct.src_trie, 0);
    print_table(rule_struct.sport_table);
    print_table(rule_struct.dport_table);*/

    //printf("%d\n", match_rule(&rule_struct, rule2));

    destroy_rules(&rule_struct);

    vector_t vector[VECTOR_SIZE];
    memset(vector, 0, VECTOR_SIZE);
    //print_bits(vector, VECTOR_SIZE);

    // data_constraint tests

    char buffer[1024];
    memset(buffer, 0, 1024);
    char *buf = buffer;

    data_constraint_t *data_c = NULL;
    data_t *data_1 = NULL;
    data_t *data_2 = NULL;
    data_t *data_3 = NULL;

    add_int_data_t(&data_1, 5);
    add_int_data_t(&data_1, 10);
    add_int_data_t(&data_1, 15);

    add_str_data_t(&data_2, 6, "pizza");
    add_str_data_t(&data_2, 6, "de la");
    add_str_data_t(&data_2, 5, "mama");

    add_int_range_data_t(&data_3, 5, 10);
    add_int_range_data_t(&data_3, 10, 15);
    add_int_range_data_t(&data_3, 15, 20);

    add_data_constraint(&data_c, INT_TYPE, 6, "test1", data_1);
    add_data_constraint(&data_c, STRING_TYPE, 6, "test2", data_2);
    add_data_constraint(&data_c, INT_RANGE_TYPE, 6, "test3", data_3);

    data_constraint_to_buffer(data_c, &buf);

    data_constraint_t *data_c_2 = NULL;
    buffer_to_data_constraint(buf, &data_c_2);

    print_data_constraint(data_c);
    print_data_constraint(data_c_2);

    destroy_data_constraint(data_c);
    destroy_data_constraint(data_c_2);

    //destroy_data_t(data, INT_TYPE);

    /*add_data_constraint(data_c, INT_TYPE, 5, "test", data);

    print_data_constraint(data_c);*/

    return 0;
}