#include <linux/types.h>
#include <linux/string.h>
#include <linux/slab.h>

typedef struct interval
{
	int start;
	int end;
} interval_t;

typedef struct string_value
{
	uint8_t str_len;
	char *str;
} string_value_t;

typedef struct data
{
	union value 
	{
		int int_value;
		string_value_t str_value;
		interval_t int_range; 
	} value_t;
	struct data *next;
} data_t;

enum data_type { 
	INT_TYPE = 0, 
	STRING_TYPE = 1, 
	INT_RANGE = 2 
};

typedef struct data_constraint
{
	enum data_type type;
	uint8_t field_len;
	char *field;
	data_t *data;
	struct data_constraint *next;
} data_constraint_t;

void destroy_data_t(data_t *data, uint8_t type);

int buffer_to_data_t(data_t *data, uint8_t type, char *buffer);

void destroy_data_constraint(data_constraint_t *data_c);

int buffer_to_data_constraint(data_constraint_t *data_c, char *msg);

int data_constraint_to_buffer(data_constraint_t *data_c, char *msg);

int add_int_data_t(data_t *data, int int_value);

int add_str_data_t(data_t *data, char *str_value);

int add_int_range_data_t(data_t *data, int start, int end);

int add_data_constraint(data_constraint_t *data_c, uint8_t type, uint8_t field_len, char *field, data_t *data);

void print_data_constraint(data_constraint_t *data_c);