#include "handlers.h"
#include "rule.h"

extern rule_list_t *rule_list;

int add_rule_cmd(int argc, char **argv);
int remove_rule_cmd(int argc, char **argv);
int print_rules_cmd(int argc, char **argv);

handler_t handler_functions[] = {
    {"add", add_rule_cmd},
    {"remove", remove_rule_cmd},
    {"print", print_rules_cmd},
    {NULL, NULL}};

int handle_cmd(string_t *name, int argc, char **argv)
{
    handler_t *tmp;

    tmp = handler_functions;
    while (tmp->handler != NULL)
    {
        if (strlen(name) != strlen(tmp->name))
        {
            tmp++;
            continue;
        }

        if (!memcmp(name, tmp->name, strlen(name)))
        {
            tmp->handler(argc, argv);
            return HANDLED;
        }

        tmp++;
    }

    return NO_HANDLER;
}

void add_usage()
{
    printf("Usage: add --src [IP] --dst [IP] --sp [PORT] --dp [PORT] --action [TYPE]\n");
}

int add_rule_cmd(int argc, char **argv)
{
    int opt = 0;
    int long_index = 0;
    uint8_t src = -1, dst = -1, sp = -1, dp = -1, act = -1;

    rule_t *rule = (rule_t *)malloc(sizeof(rule_t));
    if (!rule)
        return -1;
    memset(rule, 0, sizeof(rule_t));
    rule->index = rule_list->index;

    static struct option long_options[] = {
        {"src", required_argument, 0, 'a'},
        {"dst", required_argument, 0, 'b'},
        {"sport", required_argument, 0, 'c'},
        {"dport", required_argument, 0, 'd'},
        {"action", required_argument, 0, 'e'},
        {NULL, 0, NULL, 0}};

    optind = 1;
    while ((opt = getopt_long(argc, argv, "a:b:c:d:",
                              long_options, &long_index)) != -1)
    {
        switch (opt)
        {
        case 'a':
            src = 0;
            parse_ip(optarg, &rule->src, &rule->src_bm);
            break;
        case 'b':
            dst = 0;
            parse_ip(optarg, &rule->dst, &rule->dst_bm);
            break;
        case 'c':
            sp = 0;
            parse_port(optarg, &rule->sport, &rule->not_sport);
            break;
        case 'd':
            dp = 0;
            parse_port(optarg, &rule->dport, &rule->not_dport);
            break;
        case 'e':
            act = 0;
            parse_action(optarg, &rule->action);
            break;
        default:
            add_usage();
            free(rule);
            return -1;
        }
    }

    if (src | dst | sp | dp | act)
    {
        add_usage();
        free(rule);
        return -1;
    }

    insert_rule(rule_list, rule);

    /*if (send_msg(A_RULE, &rule, sizeof(rule_t)))
    {
        return -1;
    }*/

    return 0;
}

void remove_usage()
{
    printf("Usage: remove --index [INDEX]\n");
}

int remove_rule_cmd(int argc, char **argv)
{
    int opt = 0;
    int long_index = 0;
    int index = -1;
    rule_t *rule;

    static struct option long_options[] = {
        {"index", required_argument, 0, 'i'},
        {NULL, 0, NULL, 0}};

    optind = 1;
    while ((opt = getopt_long(argc, argv, "i:",
                              long_options, &long_index)) != -1)
    {
        switch (opt)
        {
        case 'i':
            index = atoi(optarg) - 1;
            break;
        default:
            remove_usage();
            return -1;
        }
    }

    if (index < 0)
    {
        remove_usage();
        return -1;
    }

    rule = search_rule(rule_list, index);

    /*if (send_msg(R_RULE, &rule, sizeof(rule_t)))
    {
        return -1;
    }*/

    remove_rule(rule_list, index);

    return 0;
}

int print_rules_cmd(int argc, char **argv)
{
    print_rule_list(rule_list);
    return 0;
}