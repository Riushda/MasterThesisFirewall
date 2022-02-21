#include "data.h"

typedef struct data_constraint
{
	enum data_type type;
	uint8_t field_len;
	char *field;
	data_t *data;
	vector_t vector[VECTOR_SIZE]; // contains all rules constrained by this constraint
	struct data_constraint *next;
} data_constraint_t;

/* convert buffer to struct functions */

int buffer_to_data_constraint(char *buf, uint16_t index, data_constraint_t **data_c);

/* convert struct to buffer functions */

int data_constraint_to_buffer(data_constraint_t *data_c, char **buf);

/* add struct functions */

int add_data_constraint(data_constraint_t **data_c, uint8_t type, uint8_t field_len, char *field, data_t *data, uint16_t index);

/* struct destroy functions */

int remove_data_constraint(data_constraint_t **data_c, uint16_t index);

void destroy_all_data_constraint(data_constraint_t *data_c);

/* print functions */

void print_data_constraint(data_constraint_t *data_c);