#include "rule.h"
#include "htable.h"

#define TABLE_SIZE 16

struct item *table[TABLE_SIZE];

int main(int argc, char *argv[])
{
    struct rule *match;
    match = (struct rule *)malloc(sizeof(struct rule));
    parse_ip("192.168.1.15", &match->src);
    parse_ip("192.168.1.4", &match->dst);
    match->sport = htons(5353);
    match->dport = htons(2323);

    insert_item((unsigned char *)match, table, TABLE_SIZE);
    if (search_item((unsigned char *)match, table, TABLE_SIZE) != NULL)
    {
        printf("Matched");
    }
    free_table(table, TABLE_SIZE);
    free(match);

    return 0;
}