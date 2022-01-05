#include <stdio.h>
#include "utils.h"
#include "handlers.h"

int main()
{
  char line[100];
  FILE *fp = stdin;
  int argc;
  char **argv;

  fgets(line, 100, fp);

  argc = count_args(line);

  int *lengths = (int *)malloc(sizeof(int) * argc);
  if (lengths == NULL)
  {
    return -1;
  }
  memset(lengths, 0, sizeof(int) * argc);

  arg_lengths(line, argc, lengths);

  argv = (char **)malloc(argc * sizeof(char *));
  for (int i = 0; i < argc; i++)
  {
    argv[i] = (char *)malloc(lengths[i] + 1);
    if (argv[i] == NULL)
    {
      return -1;
    }
  }

  arg_values(line, argc, lengths, argv);

  handle_cmd(argv[0], argc, argv);

  free(lengths);
  for (int i = 0; i < argc; i++)
  {
    //printf("%s\n", argv[i]);
    free(argv[i]);
  }
  free(argv);

  return 0;
}