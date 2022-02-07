#include "data_constraint.h"

typedef struct payload
{
	enum data_type type;
	uint8_t field_len;
	char *field;
	data_t *data;
} payload_t;

typedef struct abstract_packet
{
	int src;
    int dst;
    short sport;
    short dport;
	payload_t *payload;
} abstract_packet_t;

/* convert buffer to struct functions */

int buffer_to_payload(char *buf, payload_t **payload);

int buffer_to_abstract_packet(char *buf, abstract_packet_t **packet);

/* convert struct to buffer functions */

int payload_to_buffer(payload_t *payload, char **buf);

int abstract_packet_to_buffer(abstract_packet_t *packet, char **buf);

/* create struct functions */

int create_payload(payload_t **payload, uint8_t type, uint8_t field_len, char *field, data_t *data);

int create_abstract_packet(abstract_packet_t **packet, int src, int dst, short sport, short dport, payload_t *payload);

/* struct destroy functions */

void destroy_payload(payload_t *payload);

void destroy_abstract_packet(abstract_packet_t *packet);

/* print functions */

void print_payload(data_t *data, uint8_t type);

void print_abstract_packet(abstract_packet_t *packet);