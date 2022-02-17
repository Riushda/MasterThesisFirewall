#include "rule.h"

int main(){

    rule_t rule;
    rule_struct_t rule_struct;
    memset(&rule_struct, 0, sizeof(rule_struct_t));
    memset(&rule, 0, sizeof(rule_t));

    // rule

    parse_ip("192.168.1.104/24", &rule.src, &rule.src_bm);
    parse_ip("192.168.1.230/24", &rule.dst, &rule.dst_bm);
    parse_port("*", &rule.sport, &rule.not_sport);
    parse_port("22", &rule.dport, &rule.not_dport);
    rule.index = 1;
    rule.action = 1;
    print_rule(rule);

    char buffer[1024];
    memset(buffer, 0, 1024);
    char *buf = buffer;

    data_constraint_t *data_c = NULL;
    data_t *data_1 = NULL;

    char value[7];
    uint8_t str_len = 6;
    memcpy(value, &str_len, 1);
    memcpy(value+1, "friend", 6);

    add_data_t(&data_1, STRING_TYPE, 0, NULL, value);

    add_data_constraint(&data_c, STRING_TYPE, 5, "hello", data_1, 1);
    data_constraint_to_buffer(data_c, &buf);

    init_rules(&rule_struct);

    insert_rule_and_constraint(&rule_struct, rule, buf);

    // packet

    abstract_packet_t packet;
    memset(&packet, 0, sizeof(abstract_packet_t));

    parse_ip("192.168.1.204/32", &packet.src, &packet.src_bm);
    parse_ip("192.168.1.130/32", &packet.dst, &packet.dst_bm);
    parse_port("22", &packet.sport, NULL);
    parse_port("22", &packet.dport, NULL);

    content_t *content = NULL;
    data_t *data_2 = NULL;

    char value2[7];
    uint8_t str_len2 = 6;
    memcpy(value2, &str_len2, 1);
    memcpy(value2+1, "friend", 6);

    add_data_t(&data_2, STRING_TYPE, 5, "hello", value2);

    create_content(&content, STRING_TYPE, 4, "test", data_2);

    create_abstract_packet(&packet, packet.src, packet.dst, packet.sport, packet.dport, packet.src_bm, packet.dst_bm, content);

    print_abstract_packet(&packet);

    // match

    printf("RULE MATCHED : %d\n", match_rule(&rule_struct, &packet, 1));

    print_data_constraint(rule_struct.data_c);
    remove_rule(&rule_struct, rule);
    printf("AFTER REMOVE : \n");
    print_data_constraint(rule_struct.data_c);

    destroy_rules(&rule_struct);
    destroy_abstract_packet(&packet);
    destroy_all_data_constraint(data_c);

    // data_constraint tests

    /*char buffer[1024];
    memset(buffer, 0, 1024);
    char *buf = buffer;

    data_constraint_t *data_c = NULL;
    data_t *data_1 = NULL;
    data_t *data_2 = NULL;
    data_t *data_3 = NULL;
    data_t *data_4 = NULL;

    add_int_data_t(&data_1, 5);
    add_int_data_t(&data_1, 10);
    add_int_data_t(&data_1, 15);

    add_str_data_t(&data_2, 6, "pizza");
    add_str_data_t(&data_2, 6, "de la");
    add_str_data_t(&data_2, 5, "mama");

    add_int_range_data_t(&data_3, 5, 10);
    add_int_range_data_t(&data_3, 10, 15);
    add_int_range_data_t(&data_3, 15, 20);

    //add_int_data_t(&data_4, 15);
    //add_str_data_t(&data_4, 5, "mama");
    add_int_range_data_t(&data_4, 15, 20);

    add_data_constraint(&data_c, INT_TYPE, 6, "test1", data_1, 1);
    add_data_constraint(&data_c, STRING_TYPE, 6, "test2", data_2, 1);
    add_data_constraint(&data_c, INT_RANGE_TYPE, 6, "test3", data_3, 1);
    add_data_constraint(&data_c, INT_RANGE_TYPE, 6, "test3", data_4, 2);

    data_constraint_to_buffer(data_c, &buf);

    data_constraint_t *data_c_2 = NULL;
    buffer_to_data_constraint(buf, 2, &data_c_2);

    print_data_constraint(data_c);
    remove_data_constraint(&data_c, 1);
    remove_data_constraint(&data_c, 1);
    printf("AFTER REMOVE : \n");
    print_data_constraint(data_c);

    destroy_all_data_constraint(data_c);
    destroy_all_data_constraint(data_c_2); */

    /*data_t *data = NULL;
    int type = INT_RANGE_TYPE;

    //int value = 5;

    //char value[9];
    //uint8_t str_len = 8;
    //memcpy(value, &str_len, 1);
    //memcpy(value+1, "MONSIEUR", 8);

    char value[8];
    int start = 5;
    int end = 10;
    memcpy(value, &start, sizeof(int));
    memcpy(value+sizeof(int), &end, sizeof(int));

    int err = add_data_t(&data, type, 5, "HELLO", value);
    printf("error : %d\n", err);

    print_data_t(data, type);

    destroy_data_t(data, type);*/

    return 0;
}