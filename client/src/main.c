#include "htable.h"
#include <stdio.h>

int main()
{
  /*int value;
  struct h_table t2;
  init_table(&t2, 2);
  insert_pair("test", &value, &t2);*/

  struct h_table t1;
  init_table(&t1, 3);
  char *s1 = "abc";
  char *s2 = "def";
  char *s3 = "hij";
  insert_pair(s1, "", &t1);

  //struct pair *p1 = search_pair("test", &t1);

  //printf("%s\n", p1->key);

  //printf("%d\n", t1.c_size);

  display(&t1);

  insert_pair(s2, "", &t1);

  display(&t1);

  insert_pair(s3, "", &t1);

  display(&t1);

  remove_pair(s1, &t1);

  display(&t1);

  remove_pair(s2, &t1);

  display(&t1);

  //struct pair *p2 = search_pair("test", (struct h_table *)p1->value);

  //printf("%s\n", p2->key);

  remove_pair(s3, &t1);

  display(&t1);

  //p1 = search_pair("test", &t1);

  //printf("%d\n", p1 == NULL);

  destroy_table(&t1);
  //destroy_table(&t2);

  return 0;
}