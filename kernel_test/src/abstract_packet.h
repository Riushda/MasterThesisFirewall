#include "rule.h"

typedef struct payload
{
	enum data_type type;
	uint8_t field_len;
	char *field;
	data_t *data;
} payload_t;

typedef struct abstract_packet
{
	rule_t rule;
	payload_t *payload;
} abstract_packet_t;

/* create struct functions */

int create_payload(payload_t **payload, uint8_t type, uint8_t field_len, char *field, data_t *data);

int create_abstract_packet(abstract_packet_t **packet, rule_t rule, payload_t *payload);

/* struct destroy functions */

void destroy_payload(payload_t *payload);

void destroy_abstract_packet(abstract_packet_t *packet);

/* print functions */

void print_payload(payload_t *payload);

void print_abstract_packet(abstract_packet_t *packet);