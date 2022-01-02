#include "utils.h"

void print_bits(size_t const size, void const *const ptr)
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