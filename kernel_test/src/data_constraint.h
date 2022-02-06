#include <inttypes.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

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

typedef union value 
{
	int int_value;
	string_value_t str_value;
	interval_t int_range; 
} value_t;

typedef struct data
{	
	value_t value;
	struct data *next;
} data_t;

enum data_type { 
	INT_TYPE = 0, 
	STRING_TYPE = 1, 
	INT_RANGE_TYPE = 2 
};

typedef struct data_constraint
{
	enum data_type type;
	uint8_t field_len;
	char *field;
	data_t *data;
	struct data_constraint *next;
} data_constraint_t;

/* convert buffer to struct functions */

int buffer_to_data_t(data_t *data, uint8_t type, char *buffer);

int buffer_to_data_constraint(data_constraint_t *data_c, char *msg);

/* convert struct to buffer functions */

int data_t_to_buffer(data_t *data, uint8_t type, char *buffer);

int data_constraint_to_buffer(data_constraint_t *data_c, char *msg);

/* add struct functions */

int add_int_data_t(data_t **data, int int_value);

int add_str_data_t(data_t **data, uint8_t str_len, char *str);

int add_int_range_data_t(data_t **data, int start, int end);

int add_data_constraint(data_constraint_t **data_c, uint8_t type, uint8_t field_len, char *field, data_t *data);

/* struct destroy functions */

void destroy_data_t(data_t *data, uint8_t type);

void destroy_data_constraint(data_constraint_t *data_c);

/* print functions */

void print_data_t(data_t *data, uint8_t type);

void print_data_constraint(data_constraint_t *data_c);