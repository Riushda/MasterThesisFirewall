#include "utils.h"

void print_bits(size_t const size, void const *const ptr)
{
    unsigned char *b = (unsigned char *)ptr;
    unsigned char byte;
    int i, j;

    for (i = size - 1; i >= 0; i--)
    {
        for (j = 7; j >= 0; j--)
        {
            byte = (b[i] >> j) & 1;
            printf("%u", byte);
        }
    }
    puts("");
}

int remove_white_spaces(char *str)
{
    int i = 0, j = 0;
    while (str[i])
    {
        if (str[i] != ' ')
            str[j++] = str[i];
        i++;
    }
    str[j] = '\0';

    return 0;
}

int count_args(char *line)
{
    int count;
    char *current;
    int is_new_arg;

    current = line;
    count = 0;

    if (*current != '\0' && *current != ' ')
        count++;

    while (*current != '\0')
    {
        is_new_arg = 0;
        while (*current == ' ')
        {
            if (!is_new_arg)
            {
                is_new_arg = 1;
                count++;
            }
            current++;
        }
        current++;
    }

    return count;
}

void arg_lengths(char *line, int argc, int *lengths)
{
    char *current;
    int is_new_arg;
    int i;

    current = line;
    i = -1;

    if (*current != '\0' && *current != ' ')
        i++;

    while (*current != '\0')
    {
        is_new_arg = 0;
        while (*current == ' ')
        {
            if (!is_new_arg)
            {
                is_new_arg = 1;
                i++;
            }
            current++;
        }
        current++;
        lengths[i]++;
    }

    lengths[argc - 1]--;
}

void arg_values(char *line, int argc, int *lengths, char **argv)
{
    char *tmp_line;
    char *no_space;

    tmp_line = (char *)malloc(strlen(line) + 1);
    strcpy(tmp_line, line);
    remove_white_spaces(tmp_line);

    no_space = tmp_line;

    for (int i = 0; i < argc; i++)
    {
        memcpy(argv[i], no_space, lengths[i]);
        *(argv[i] + lengths[i]) = '\0';
        no_space += lengths[i];
    }

    free(tmp_line);
}
