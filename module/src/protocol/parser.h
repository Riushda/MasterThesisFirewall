#include "../rule/rule.h"

typedef struct format
{
	uint8_t offset; // to skip first symbol like ? or { 
	char *splitter; // split group into field value
	char *delimiter; // split groups
	char *end; // to deal with } json for instance at the end
} format_t;

int create_format(format_t **pattern, uint8_t offset, char *splitter, char *delimiter, char *end);

void destroy_format(format_t *pattern);

int decode_payload(format_t *pattern, char *buf, uint8_t buf_len, data_t **payload);

void print_format(format_t *pattern);