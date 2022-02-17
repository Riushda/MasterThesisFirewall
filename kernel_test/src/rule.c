#include "rule.h"

int parse_not(string_t *str_not, bool_t *not_v)
{
    if(not_v!=NULL){ /// can be NULL with abstract packet

        memset(not_v, 0, sizeof(bool_t));

        if (!memcmp(str_not, "!", 1))
        {
            *not_v = 1;
            return 1;
        }
        else
        {
            *not_v = 0;
            return 0;
        }
    }

    return 0;
}

int parse_ip(string_t *str_ip, int *ip, bitmask_t *bitmask)
{
    struct in_addr addr;
    char str[strlen(str_ip)];
    char *token;
    const char delimiter[2] = "/";

    memset(ip, 0, sizeof(int));
    strcpy(str, str_ip);

    if (strlen(str_ip) == 1) /* 7 is the minimum valid length for an IP */
    {
        if (!memcmp(str, "*", 1))
        {
            memset(ip, 0, sizeof(int));
            return 0;
        }
        else
        {
            return -1;
        }
    }

    token = strtok(str, delimiter);
    if (token)
    {
        if (!inet_aton(token, &addr))
        {
            return -1;
        }
    }

    memcpy(ip, &addr, sizeof(struct in_addr));
    *ip = htonl(*ip);

    token = strtok(NULL, delimiter);
    if (token)
    {
        *bitmask = atoi(token);
        if (!*bitmask)
            return -1;
    }
    else
    {
        *bitmask = 32;
    }

    return 0;
}

void parse_port(string_t *str_port, short *port, bool_t *not_v)
{
    short hport;
    char *str;

    str = str_port;
    memset(port, 0, sizeof(short));

    if (parse_not(str, not_v))
    {
        str++;
    }

    if (!memcmp(str, "*", 1))
    {
        memset(port, 0, sizeof(short));
        return;
    }

    hport = htons(atoi(str));

    memcpy(port, &hport, sizeof(short));
}

void print_rule(rule_t rule)
{
    struct in_addr addr;
    int src;
    int dst;

    if (rule.not_src)
    {
        printf("!");
    }

    src = ntohl(rule.src);
    memcpy(&addr, &src, sizeof(struct in_addr));
    printf("Src: %s/%d ", inet_ntoa(addr), rule.src_bm);

    if (rule.not_dst)
    {
        printf("!");
    }

    dst = ntohl(rule.dst);
    memcpy(&addr, &dst, sizeof(struct in_addr));
    printf("Dst: %s/%d ", inet_ntoa(addr), rule.dst_bm);

    if (rule.not_sport)
    {
        printf("!");
    }

    printf("Sport: %d ", ntohs(rule.sport));

    if (rule.not_dport)
    {
        printf("!");
    }

    printf("Dport: %d ", ntohs(rule.dport));

    printf("action : %d ", rule.action);

    printf("index : %d\n", rule.index);
}

int init_rules(rule_struct_t *rule_struct)
{
    rule_struct->src_trie = (trie_t *)malloc(sizeof(trie_t));
    if (init_trie(rule_struct->src_trie))
        return -1;

    rule_struct->dst_trie = (trie_t *)malloc(sizeof(trie_t));
    if (init_trie(rule_struct->dst_trie))
        return -1;

    rule_struct->sport_table = (h_table_t *)malloc(sizeof(h_table_t));
    if (init_table(rule_struct->sport_table, TABLE_SIZE))
        return -1;

    rule_struct->dport_table = (h_table_t *)malloc(sizeof(h_table_t));
    if (init_table(rule_struct->dport_table, TABLE_SIZE))
        return -1;

    rule_struct->data_c = NULL; // will be malloc during first insert

    memset(rule_struct->actions, 0, VECTOR_SIZE);
    return 0;
}

int insert_rule(rule_struct_t *rule_struct, rule_t rule)
{
    h_key_t key[KEY_SIZE];

    if (insert_node(rule_struct->src_trie, rule.src, rule.src_bm, rule.index))
        return -1;
    if (insert_node(rule_struct->dst_trie, rule.dst, rule.dst_bm, rule.index))
        return -1;

    memset(key, 0, KEY_SIZE);
    memcpy(key, &rule.not_sport, sizeof(bool_t));
    memcpy(key + sizeof(bool_t), &rule.sport, sizeof(short));
    if (insert_hash(rule_struct->sport_table, key, rule.index))
        return -1;

    memset(key, 0, KEY_SIZE);
    memcpy(key, &rule.not_dport, sizeof(bool_t));
    memcpy(key + sizeof(bool_t), &rule.dport, sizeof(short));
    if (insert_hash(rule_struct->dport_table, key, rule.index))
        return -1;

    if (rule.action)
        set_bit_v(rule_struct->actions, rule.index);

    return 0;
}

int insert_rule_and_constraint(rule_struct_t *rule_struct, rule_t rule, char *buf)
{
    if(insert_rule(rule_struct, rule))
        return -1;

    if(buffer_to_data_constraint(buf, rule.index, &(rule_struct->data_c)))
        return -1;

    return 0;
}

int remove_rule(rule_struct_t *rule_struct, rule_t rule)
{
    h_key_t key[KEY_SIZE];

    remove_node(rule_struct->src_trie, rule.src, rule.src_bm, rule.index);
    remove_node(rule_struct->dst_trie, rule.dst, rule.dst_bm, rule.index);

    memset(key, 0, KEY_SIZE);
    memcpy(key, &rule.not_sport, sizeof(bool_t));
    memcpy(key + sizeof(bool_t), &rule.sport, sizeof(short));
    remove_hash(rule_struct->sport_table, key, rule.index);

    memset(key, 0, KEY_SIZE);
    memcpy(key, &rule.not_dport, sizeof(bool_t));
    memcpy(key + sizeof(bool_t), &rule.dport, sizeof(short));
    remove_hash(rule_struct->dport_table, key, rule.index);

    remove_data_constraint(&(rule_struct->data_c), rule.index);

    unset_shift_v(rule_struct->actions, rule.index);

    return 0;
}

vector_t *match_port(h_table_t *table, short port)
{
    h_key_t key[KEY_SIZE];
    vector_t *result_any;
    vector_t *result_port;
    vector_t *result_not_port;

    memset(key, 0, KEY_SIZE);
    //memset(key, 2, sizeof(bool_t)); => don't remember why we do this but removing it fix * matching for port
    result_any = search_hash(table, key);

    //memset(key, 0, sizeof(bool_t)); => don't remember why we do this
    memcpy(key + sizeof(bool_t), &port, sizeof(short));
    result_port = or_v(result_any, search_hash(table, key));

    memset(key, 1, sizeof(bool_t));
    result_not_port = or_v(result_port, search_hash(table, key));

    free(result_port);

    //print_bits(result_not_port, VECTOR_SIZE);

    return result_not_port;
}

int first_constrained_match_index(abstract_packet_t *packet, data_constraint_t *data_c, vector_t *vector){
    int i;

    for (i = 0; i < VECTOR_SIZE; i++)
    {
        if (is_set_v(vector, i)){
            if(!match_data_constraint(packet->content, data_c, i))
                return i;
        }
            
    }

    return -1;
}

int match_rule(rule_struct_t *rule_struct, abstract_packet_t *packet, bool_t constraint)
{
    vector_t *result_src;
    vector_t *result_dst;
    vector_t *result_sport;
    vector_t *match_sport;
    vector_t *result_dport;
    vector_t *match_dport;
    short rule_index;

    bool_t temp;
    uint8_t match;

    result_src = search_node(rule_struct->src_trie, packet->src);
    result_dst = and_v(result_src, search_node(rule_struct->dst_trie, packet->dst));
    match_sport = match_port(rule_struct->sport_table, packet->sport);
    result_sport = and_v(result_dst, match_sport);
    match_dport = match_port(rule_struct->dport_table, packet->dport);
    result_dport = and_v(result_sport, match_dport);

    if(constraint){ // if constrained matching
        // remove rules index in result_dport with constraint not matching the packet until a matching one is found
        rule_index = first_constrained_match_index(packet, rule_struct->data_c, result_dport);
    }
    else{ // if simple ip matching
        rule_index = first_match_index(result_dport);
    }

    free(result_dst);
    free(result_sport);
    free(result_dport);
    free(match_sport);
    free(match_dport);

    if (rule_index != -1 && rule_index < VECTOR_SIZE){
        temp = is_set_v(rule_struct->actions, rule_index);
        
        memset(&match, 0, sizeof(uint8_t));
        memcpy(&match, &temp, sizeof(uint8_t));
        if(match)
            return rule_index;
    }

    return -1;
}

void destroy_rules(rule_struct_t *rule_struct)
{
    destroy_trie(rule_struct->src_trie);
    free(rule_struct->src_trie);

    destroy_trie(rule_struct->dst_trie);
    free(rule_struct->dst_trie);

    destroy_table(rule_struct->sport_table);
    free(rule_struct->sport_table);

    destroy_table(rule_struct->dport_table);
    free(rule_struct->dport_table);

    destroy_all_data_constraint(rule_struct->data_c);
}

int rule_to_buffer(rule_t *rule, unsigned char *buffer)
{
    int offset;
    offset = 0;

    memcpy(buffer + offset, &rule->src, sizeof(rule->src));
    offset += sizeof(rule->src);
    memcpy(buffer + offset, &rule->dst, sizeof(rule->dst));
    offset += sizeof(rule->dst);
    memcpy(buffer + offset, &rule->sport, sizeof(rule->sport));
    offset += sizeof(rule->sport);
    memcpy(buffer + offset, &rule->dport, sizeof(rule->dport));
    offset += sizeof(rule->dport);

    return offset;
}

int buffer_to_rule(char *buf, rule_t *rule){
    
    int offset = 0;
    // src 

    memcpy(&(rule->src), buf+offset, sizeof(int));
    rule->src = htonl(rule->src);
    offset += sizeof(int);

    memcpy(&(rule->src_bm), buf+offset, sizeof(bitmask_t));
    offset += sizeof(bitmask_t);

    memcpy(&(rule->sport), buf+offset, sizeof(short));
    rule->sport = rule->sport;
    offset += sizeof(short);

    memcpy(&(rule->not_sport), buf+offset, sizeof(bool_t));
    offset += sizeof(bool_t);

    // dst 

    memcpy(&(rule->dst), buf+offset, sizeof(int));
    rule->dst = htonl(rule->dst);
    offset += sizeof(int);

    memcpy(&(rule->dst_bm), buf+offset, sizeof(bitmask_t));
    offset += sizeof(bitmask_t);

    memcpy(&(rule->dport), buf+offset, sizeof(short));
    rule->dport = rule->dport;
    offset += sizeof(short);

    memcpy(&(rule->not_dport), buf+offset, sizeof(bool_t));
    offset += sizeof(bool_t);

    // action

    memcpy(&(rule->action), buf+offset, sizeof(bool_t));
    offset += sizeof(bool_t);

    // index

    memcpy(&(rule->index), buf+offset, sizeof(short));
    offset += sizeof(short);


    return offset;
}