#include "rule.h"

extern rule_list_t *rule_list;

int main()
{
  rule_list = (rule_list_t *)malloc(sizeof(rule_list_t));
  memset(rule_list, 0, sizeof(rule_list_t));

  rule_t *r1 = (rule_t *)malloc(sizeof(rule_t));
  memset(r1, 0, sizeof(rule_t));

  init_rule_list(rule_list);

  parse_ip("127.0.0.1/24", &r1->src, &r1->src_bm);
  parse_ip("127.0.0.1/24", &r1->dst, &r1->dst_bm);
  parse_port("22", &r1->sport, &r1->not_sport);
  parse_port("22", &r1->dport, &r1->not_dport);
  r1->index = rule_list->index;
  insert_rule(rule_list, r1);

  rule_t *r2 = (rule_t *)malloc(sizeof(rule_t));
  memset(r2, 0, sizeof(rule_t));

  parse_ip("128.0.0.1/24", &r2->src, &r2->src_bm);
  parse_ip("127.0.0.1/24", &r2->dst, &r2->dst_bm);
  parse_port("22", &r2->sport, &r2->not_sport);
  parse_port("22", &r2->dport, &r2->not_dport);
  r2->index = rule_list->index;
  insert_rule(rule_list, r2);

  rule_t *r3 = (rule_t *)malloc(sizeof(rule_t));
  memset(r3, 0, sizeof(rule_t));

  parse_ip("129.0.0.1/24", &r3->src, &r3->src_bm);
  parse_ip("127.0.0.1/24", &r3->dst, &r3->dst_bm);
  parse_port("22", &r3->sport, &r3->not_sport);
  parse_port("22", &r3->dport, &r3->not_dport);
  r3->index = rule_list->index;
  insert_rule(rule_list, r3);

  remove_rule(rule_list, 2);

  print_rule_list(rule_list);
  destroy_rule_list(rule_list);
}