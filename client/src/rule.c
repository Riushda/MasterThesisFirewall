#include "rule.h"

rule_list_t *rule_list;

int parse_not(string_t *str_not, bool_t *not_v)
{
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

void parse_action(string_t *str_action, bool_t *action)
{
    if (!strcasecmp(str_action, "allow") || !strcasecmp(str_action, "a") || !strcasecmp(str_action, "1"))
        *action = 1;
    else
        *action = 0;
}

void print_rule(rule_t rule)
{
    struct in_addr addr;
    int src;
    int dst;

    fflush(stdout);

    printf("%d | ", rule.index + 1);

    if (rule.not_src)
    {
        printf("!");
    }

    src = ntohl(rule.src);
    memcpy(&addr, &src, sizeof(struct in_addr));
    printf("--src %s/%d ", inet_ntoa(addr), rule.src_bm);

    if (rule.not_dst)
    {
        printf("!");
    }

    dst = ntohl(rule.dst);
    memcpy(&addr, &dst, sizeof(struct in_addr));
    printf("--dst %s/%d ", inet_ntoa(addr), rule.dst_bm);

    if (rule.not_sport)
    {
        printf("!");
    }

    printf("--sport %d ", ntohs(rule.sport));

    if (rule.not_dport)
    {
        printf("!");
    }

    printf("--sport %d ", ntohs(rule.dport));

    if (rule.action)
        printf("--action ALLOW\n");
    else
        printf("--action DENY\n");
}

void init_rule_list(rule_list_t *rule_list)
{
    rule_list->head = NULL;
    rule_list->index = 0;
}

void insert_rule(rule_list_t *rule_list, rule_t *rule)
{
    rule_t *current;
    rule_t *previous;
    short index;

    current = rule_list->head;

    if (!current)
    {
        rule_list->head = rule;
        rule_list->head->next = NULL;
        rule_list->index++;
        return;
    }

    while (current != NULL)
    {
        previous = current;
        current = current->next;
    }

    previous->next = rule;
    rule->next = NULL;
    rule_list->index++;
}

void remove_rule(rule_list_t *rule_list, short index)
{
    rule_t *current;
    rule_t *previous;

    current = rule_list->head;
    previous = NULL;

    while (current != NULL)
    {
        if (current->index == index)
        {
            if (previous)
            {
                previous->next = current->next;
                free(current);
                current = previous->next;
            }
            else
            {
                rule_list->head = current->next;
                free(current);
                current = rule_list->head;
            }
            break;
        }
        previous = current;
        current = current->next;
    }

    while (current != NULL)
    {
        current->index--;
        current = current->next;
    }

    rule_list->index--;
}

rule_t *search_rule(rule_list_t *rule_list, short index)
{
    rule_t *current;

    current = rule_list->head;

    while (current != NULL)
    {
        if (current->index == index)
            return current;
        current = current->next;
    }

    return NULL;
}

void destroy_rule_list(rule_list_t *rule_list)
{
    rule_t *current;
    rule_t *next;

    current = rule_list->head;
    next = NULL;

    while (current != NULL)
    {
        next = current->next;
        free(current);
        current = next;
    }

    free(rule_list);
}

void print_rule_list(rule_list_t *rule_list)
{
    rule_t *current;

    current = rule_list->head;

    while (current != NULL)
    {
        print_rule(*current);
        current = current->next;
    }
}