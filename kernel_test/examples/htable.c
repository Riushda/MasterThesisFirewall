#include "htable.h"

int main()
{
    h_table_t htable;
    entry_t *entry;
    init_table(&htable, TABLE_SIZE);
    insert_hash(&htable, "abc", 0);
    insert_hash(&htable, "def", 1);
    insert_hash(&htable, "hij", 2);
    remove_hash(&htable, "abc", 0);
    entry = search_hash(&htable, "abc");
    printf("%s\n", entry->key);
    print_bits(entry->vector, VECTOR_SIZE);
    print_table(&htable);
    destroy_table(&htable);
    return 0;
}