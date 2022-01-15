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
    vector_t *current;

    current = vector;
    bitmask = 1 << (index % 8);

    current += ((int)index / 8);
    return (*current & bitmask) != 0;
}

void set_bit_v(vector_t *vector, short index)
{
    bitmask_t bitmask;
    vector_t *current;

    current = vector;
    bitmask = 1 << (index % 8);

    current += ((int)index / 8);
    *current |= bitmask;
}

void unset_shift_v(vector_t *vector, short index)
{
    bitmask_t bitmask;
    vector_t *current;
    vector_t old_current;
    int i;
    int offset;

    offset = (int)(index / 8);
    if (offset >= VECTOR_SIZE)
        return;

    current = vector;
    current += offset;
    old_current = *current;

    bitmask = 0;
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
    vector_t *current;
    int i;
    int sum;

    current = vector;
    sum = 0;

    for (i = 0; i < VECTOR_SIZE; i++)
    {
        sum += current[i];
    }

    return sum == 0;
}

vector_t *and_v(vector_t *vector1, vector_t *vector2)
{
    vector_t *current1;
    vector_t *current2;
    vector_t *current3;
    vector_t *result;
    int i;

    result = (vector_t *)malloc(VECTOR_SIZE);

    if (result)
    {
        memset(result, 0, VECTOR_SIZE);

        if (!vector1 | !vector2)
            return result;

        current1 = vector1;
        current2 = vector2;
        current3 = result;

        for (i = 0; i < VECTOR_SIZE; i++)
        {
            *current3 = *current1 & *current2;
            current3++, current1++, current2++;
        }
    }

    return result;
}

vector_t *or_v(vector_t *vector1, vector_t *vector2)
{
    vector_t *current1;
    vector_t *current2;
    vector_t *current3;
    vector_t *result;
    int i;

    result = (vector_t *)malloc(VECTOR_SIZE);

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

        current1 = vector1;
        current2 = vector2;
        current3 = result;

        for (i = 0; i < VECTOR_SIZE; i++)
        {
            *current3 = *current1 | *current2;
            current3++, current1++, current2++;
        }
    }

    return result;
}
