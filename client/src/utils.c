#include "utils.h"

void print_bits(void const *const ptr, size_t const size)
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
    printf("\n");
    fflush(stdout);
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

    if (*current == '\n')
        return 0;

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

int bitmask(size_t size)
{
    int i;
    int bitmask;

    if (size > 32)
        return -1;

    memset(&bitmask, 0, sizeof(int));

    for (i = 0; i < size; i++)
    {
        bitmask = (bitmask >> 1);
        bitmask |= 2147483648;
    }

    return bitmask;
}

int is_set_ip(int ip, short offset)
{
    int bitmask;
    int i;

    if (offset > 31)
        return -1;

    bitmask = 2147483648 >> offset;

    return (ip & bitmask) != 0;
}

int is_set_v(void *ptr, int index)
{
    uint8_t bitmask;
    uint8_t *current;

    current = (uint8_t *)ptr;
    bitmask = 1 << (index % 8);

    current += ((int)index / 8);
    return (*current & bitmask) != 0;
}

void set_bit_v(void *ptr, int index)
{
    uint8_t bitmask;
    uint8_t *current;

    current = (uint8_t *)ptr;
    bitmask = 1 << (index % 8);

    current += ((int)index / 8);
    *current |= bitmask;
}

void unset_shift_v(void *ptr, int index)
{
    uint8_t bitmask;
    uint8_t *current;
    uint8_t old_current;
    int i;
    int offset;

    offset = (int)(index / 8);
    if (offset >= VECTOR_SIZE)
        return;

    current = (uint8_t *)ptr;
    current += offset;
    old_current = *current;

    for (i = 0; i < 8 - (index % 8); i++)
        bitmask = (bitmask >> 1) + 128;

    /* First remove the part starting from the index */
    *current &= (2147483647 ^ bitmask);

    /* Save the part after the index */
    bitmask = bitmask << 1;
    bitmask &= old_current;

    /* Shift the part after the index and merge with part before the index */
    bitmask = bitmask >> 1;
    *current |= bitmask;

    if (offset >= VECTOR_SIZE - 1)
        return;

    /* We must be careful with the first bit of the byte because the shift won't preserve it */
    if ((*(current + 1) & 1) == 1)
    {
        *current |= 128;
    }

    /* Now we also need to shift all the bytes after the current byte */
    for (i = offset + 1; i < VECTOR_SIZE; i++)
    {
        current++;
        *current = *current >> 1;

        if (i < VECTOR_SIZE - 1 & ((*(current + 1) & 1) == 1))
            *current |= 128;
    }
}
