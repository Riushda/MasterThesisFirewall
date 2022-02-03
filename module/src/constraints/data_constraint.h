#include "int_range.h"

struct string_value{
	uint8_t payload_len;
	char *string;
} string_value_t;

union value {
	int integer_value;
	string_value_t string_value;
	interval_t int_range; 
} value_t;

struct data{
	value_t value;
	value_t *next;
} data_t;

typedef struct data_constraint
{
	enum { INT_TYPE = 0, STRING_TYPE = 1, INT_RANGE = 2 } type;
	uint8_t field_len;
	char *field;
	data_t *data;
	struct data_constraint *next
} data_constraint_t;

void create_data_constraint(data_constraint_t *data_c);

void destroy_data_constraint(data_constraint_t *data_c);