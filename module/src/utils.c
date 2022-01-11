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
            printk(KERN_CONT "%u", byte);
        }
    }
    printk(KERN_CONT "\n");
}