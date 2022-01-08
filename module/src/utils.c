#include "utils.h"

void print_bits(void const *const ptr, size_t const size)
{
    unsigned char *b = (unsigned char *)ptr;
    unsigned char byte;
    int i, j;

    for (i = 0; size > i; i++)
    {
        for (j = 0; 8 > j; j++)
        {
            byte = (b[i] >> j) & 1;
            printk(KERN_CONT "%u", byte);
        }
    }
    printk(KERN_CONT "\n");
}