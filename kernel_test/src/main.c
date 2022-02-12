#include "rule.h"

int main()
{
    /*rule_t rule;
    rule_struct_t rule_struct;
    memset(&rule_struct, 0, sizeof(rule_struct_t));
    memset(&rule, 0, sizeof(rule_t));

    parse_ip("127.0.0.1/24", &rule.src, &rule.src_bm);
    parse_ip("127.0.0.1/24", &rule.dst, &rule.dst_bm);
    parse_port("*", &rule.sport, &rule.not_sport);
    parse_port("22", &rule.dport, &rule.not_dport);
    rule.index = 1;
    rule.action = 1;

    char buffer[1024];
    memset(buffer, 0, 1024);
    char *buf = buffer;

    data_constraint_t *data_c = NULL;
    data_t *data_1 = NULL;
    add_str_data_t(&data_1, 7, "friend");
    add_data_constraint(&data_c, STRING_TYPE, 6, "hello", data_1, 1);
    data_constraint_to_buffer(data_c, &buf);

    init_rules(&rule_struct);

    insert_rule_and_constraint(&rule_struct, rule, buf);

    abstract_packet_t packet;
    memset(&packet, 0, sizeof(abstract_packet_t));

    parse_ip("127.0.0.1/24", &packet.src, &packet.src_bm);
    parse_ip("127.0.0.1/24", &packet.dst, &packet.dst_bm);
    parse_port("22", &packet.sport, NULL);
    parse_port("22", &packet.dport, NULL);

    payload_t *payload = NULL;
    data_t *data_2 = NULL;

    add_str_data_t(&data_2, 7, "friend");

    create_payload(&payload, STRING_TYPE, 6, "hello", data_2);

    create_abstract_packet(&packet, packet.src, packet.dst, packet.sport, packet.dport, packet.src_bm, packet.dst_bm, payload);

    print_abstract_packet(&packet);

    printf("IP MATCHED : %d\n", match_rule(&rule_struct, &packet));
    printf("CONSTRAINT MATCHED : %d\n", match_constraint(&rule_struct, &packet));

    print_data_constraint(rule_struct.data_c);
    remove_rule(&rule_struct, rule);
    printf("AFTER REMOVE : \n");
    print_data_constraint(rule_struct.data_c);

    destroy_rules(&rule_struct);
    destroy_abstract_packet(&packet);
    destroy_all_data_constraint(data_c);*/

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

    // test hexa to byte

    char dst[5];
    char hexa[24] = "\\x05\\x01\\x00\\x03\\x04\\x05"; // 20 = 4+5*4
    
    char len[1];
    hexa_to_byte(hexa, len, 1);

    hexa_to_byte(hexa+4, dst, (uint8_t) *len);

    for(int i=0; i<*len; i++)
        printf("dst[%d] : %d\n", i, dst[i]);

    return 0;
}