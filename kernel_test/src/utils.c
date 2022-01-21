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
    printk(KERN_INFO ""); // new line
}

bool_t is_set_ip(int ip, short offset)
{
    int bitmask;
    int i;

    if (offset > 31)
        return -1;

    bitmask = 2147483648 >> offset;

    return (ip & bitmask) != 0;
}

bool_t is_set_v(vector_t *vector, short index)
{
    bitmask_t bitmask;
    vector_t *element;

    element = vector;
    bitmask = 1 << (index % 8);

    element += ((int)index / 8);
    return (*element & bitmask) != 0;
}

void set_bit_v(vector_t *vector, short index)
{
    bitmask_t bitmask;
    vector_t *element;

    element = vector;
    bitmask = 1 << (index % 8);

    element += ((int)index / 8);
    *element |= bitmask;
}

void unset_shift_v(vector_t *vector, short index)
{
    bitmask_t bitmask;
    vector_t *element;
    vector_t old_element;
    int i;
    int offset;

    offset = (int)(index / 8);
    if (offset >= VECTOR_SIZE)
        return;

    element = vector;
    element += offset;
    old_element = *element;

    bitmask = 0;
    for (i = 0; i < 8 - (index % 8); i++)
        bitmask = (bitmask >> 1) + 128;

    /* First remove the part starting from the index */
    *element &= (2147483647 ^ bitmask);

    /* Save the part after the index */
    bitmask = bitmask << 1;
    bitmask &= old_element;

    /* Shift the part after the index and merge with part before the index */
    bitmask = bitmask >> 1;
    *element |= bitmask;

    if (offset >= VECTOR_SIZE - 1)
        return;

    /* We must be careful with the first bit of the byte because the shift won't preserve it */
    if ((*(element + 1) & 1) == 1)
    {
        *element |= 128;
    }

    /* Now we also need to shift all the bytes after the element byte */
    for (i = offset + 1; i < VECTOR_SIZE; i++)
    {
        element++;
        *element = *element >> 1;

        if (i < VECTOR_SIZE - 1 & ((*(element + 1) & 1) == 1))
            *element |= 128;
    }
}

short first_match_index(vector_t *vector)
{
    int i;

    for (i = 0; i < VECTOR_SIZE; i++)
    {
        if (is_set_v(vector, i))
            return i;
    }

    return -1;
}

bool_t is_null_v(vector_t *vector)
{
    vector_t *element;
    int i;
    int sum;

    element = vector;
    sum = 0;

    for (i = 0; i < VECTOR_SIZE; i++)
    {
        sum += element[i];
    }

    return sum == 0;
}

vector_t *and_v(vector_t *vector1, vector_t *vector2)
{
    vector_t *element1;
    vector_t *element2;
    vector_t *element3;
    vector_t *result;
    int i;

    result = (vector_t *)kmalloc(VECTOR_SIZE, GFP_KERNEL);

    if (result)
    {
        memset(result, 0, VECTOR_SIZE);

        if (!vector1 | !vector2)
            return result;

        element1 = vector1;
        element2 = vector2;
        element3 = result;

        for (i = 0; i < VECTOR_SIZE; i++)
        {
            *element3 = *element1 & *element2;
            element3++, element1++, element2++;
        }
    }

    return result;
}

vector_t *or_v(vector_t *vector1, vector_t *vector2)
{
    vector_t *element1;
    vector_t *element2;
    vector_t *element3;
    vector_t *result;
    int i;

    result = (vector_t *)kmalloc(VECTOR_SIZE, GFP_KERNEL);

    if (result)
    {
        memset(result, 0, VECTOR_SIZE);
        if (!vector1 && !vector2)
            return result;

        if (!vector1)
        {
            memcpy(result, vector2, VECTOR_SIZE);
            return result;
        }

        if (!vector2)
        {
            memcpy(result, vector1, VECTOR_SIZE);
            return result;
        }

        element1 = vector1;
        element2 = vector2;
        element3 = result;

        for (i = 0; i < VECTOR_SIZE; i++)
        {
            *element3 = *element1 | *element2;
            element3++, element1++, element2++;
        }
    }

    return result;
}
