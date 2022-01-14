#include "handlers.h"

int add_rule_cmd(int argc, char **argv);
int remove_rule_cmd(int argc, char **argv);

handler_t handler_functions[] = {
    {"add", add_rule_cmd},
    {"remove", remove_rule_cmd},
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
    printf("Usage: add --src [IP] --dst [IP] --sp [PORT] --dp [PORT]\n");
}

int add_rule_cmd(int argc, char **argv)
{
    int opt = 0;
    int long_index;
    uint8_t src = -1, dst = -1, sp = -1, dp = -1;
    int src_bm = 0, dst_bm = 0;
    rule_t rule;
    memset(&rule, 0, sizeof(rule_t));

    static struct option long_options[] = {
        {"src", required_argument, 0, 'a'},
        {"dst", required_argument, 0, 'b'},
        {"sport", required_argument, 0, 'c'},
        {"dport", required_argument, 0, 'd'},
        {NULL, 0, NULL, 0}};

    long_index = 0;
    optind = 1;
    while ((opt = getopt_long(argc, argv, "a:b:c:d:",
                              long_options, &long_index)) != -1)
    {
        switch (opt)
        {
        case 'a':
            src = 0;
            parse_ip(optarg, &rule.src, &rule.src_bm);
            break;
        case 'b':
            dst = 0;
            parse_ip(optarg, &rule.dst, &rule.dst_bm);
            break;
        case 'c':
            sp = 0;
            parse_port(optarg, &rule.sport, &rule.not_sport);
            break;
        case 'd':
            dp = 0;
            parse_port(optarg, &rule.dport, &rule.not_dport);
            break;
        default:
            add_usage();
            return -1;
        }
    }

    if (src | dst | sp | dp)
    {
        add_usage();
        return -1;
    }

    print_rule(rule);
    if (send_msg(A_RULE, &rule, sizeof(rule_t)))
    {
        return -1;
    }

    return 0;
}

void remove_usage()
{
    printf("Usage: remove --src [IP] --dst [IP] --sp [PORT] --dp [PORT]\n");
}

int remove_rule_cmd(int argc, char **argv)
{
    int opt = 0;
    int long_index;
    uint8_t src = -1, dst = -1, sp = -1, dp = -1;
    int src_bm = 0, dst_bm = 0;
    rule_t rule;
    memset(&rule, 0, sizeof(rule_t));

    static struct option long_options[] = {
        {"src", required_argument, 0, 'a'},
        {"dst", required_argument, 0, 'b'},
        {"sport", required_argument, 0, 'c'},
        {"dport", required_argument, 0, 'd'},
        {NULL, 0, NULL, 0}};

    long_index = 0;
    optind = 1;
    while ((opt = getopt_long(argc, argv, "a:b:c:d:",
                              long_options, &long_index)) != -1)
    {
        switch (opt)
        {
        case 'a':
            src = 0;
            parse_ip(optarg, &rule.src, &rule.src_bm);
            break;
        case 'b':
            dst = 0;
            parse_ip(optarg, &rule.dst, &rule.dst_bm);
            break;
        case 'c':
            sp = 0;
            parse_port(optarg, &rule.sport, &rule.not_sport);
            break;
        case 'd':
            dp = 0;
            parse_port(optarg, &rule.dport, &rule.not_dport);
            break;
        default:
            remove_usage();
            return -1;
        }
    }

    if (src | dst | sp | dp)
    {
        remove_usage();
        return -1;
    }

    print_rule(rule);
    if (send_msg(R_RULE, &rule, sizeof(rule_t)))
    {
        return -1;
    }

    return 0;
}