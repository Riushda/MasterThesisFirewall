#include <inttypes.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "utils.h"
#include "constant.h"

enum data_type {
	SUBJECT_TYPE = 0, // only match the topic  
	INT_TYPE = 1, 
	STRING_TYPE = 2, 
	INT_RANGE_TYPE = 3 
};

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
	
	/* only used by abstract packet */
	enum data_type type;
	uint8_t field_len;
	char *field;
} data_t;

int buffer_to_data_t(char *buf, uint8_t type, data_t **data);

int data_t_to_buffer(data_t *data, uint8_t type, char **buf);

int add_data_t(data_t **data, int type, uint8_t field_len, char *field, void *value);

int contains_data_t(data_t *src, data_t *dst, uint8_t type);

void destroy_data_t(data_t *data, uint8_t type);

void print_data_t(data_t *data, uint8_t type);