#include <signal.h>
#include "netlink.h"
#include "utils.h"
#include "handlers.h"

extern rule_list_t *rule_list;

void INThandler(int);

int main()
{
  signal(SIGINT, INThandler);

  char line[100];
  FILE *fp = stdin;
  int argc;
  char **argv;

  rule_list = (rule_list_t *)malloc(sizeof(rule_list_t));
  memset(rule_list, 0, sizeof(rule_list_t));

  /*if (open_netlink())
  {
    return -1;
  }*/

  while (1)
  {
    fgets(line, 100, fp);
    argc = count_args(line);

    if (argc <= 0)
      continue;

    int *lengths = (int *)malloc(sizeof(int) * argc);
    if (lengths == NULL)
    {
      destroy_rule_list(rule_list);
      return -1;
    }

    memset(lengths, 0, sizeof(int) * argc);
    arg_lengths(line, argc, lengths);

    argv = (char **)malloc(argc * sizeof(char *));
    if (argv == NULL)
    {
      destroy_rule_list(rule_list);
      free(lengths);
      return -1;
    }
    for (int i = 0; i < argc; i++)
    {
      argv[i] = (char *)malloc(lengths[i] + 1);
      if (argv[i] == NULL)
      {
        destroy_rule_list(rule_list);
        free(lengths);
        free(argv);
        return -1;
      }
    }

    arg_values(line, argc, lengths, argv);
    handle_cmd(argv[0], argc, argv);

    free(lengths);
    for (int i = 0; i < argc; i++)
    {
      free(argv[i]);
    }
    free(argv);
  }

  return 0;
}

void INThandler(int sig)
{
  char c;

  signal(sig, SIG_IGN);
  printf("\nYou just hit Ctrl-C,\n"
         "Do you really want to quit? [y/n] ");
  c = getchar();
  if (c == 'y' || c == 'Y')
  {
    //close_netlink();
    destroy_rule_list(rule_list);
    exit(0);
  }
  else
    signal(SIGINT, INThandler);
  getchar();
}