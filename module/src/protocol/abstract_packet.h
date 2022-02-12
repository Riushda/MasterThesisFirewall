#include "../constraints/data_constraint.h"

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
	bitmask_t src_bm;
    bitmask_t dst_bm;
	payload_t *payload;
} abstract_packet_t;

/* create struct functions */

int create_payload(payload_t **payload, uint8_t type, uint8_t field_len, char *field, data_t *data);

int create_abstract_packet(abstract_packet_t *packet, int src, int dst, short sport, short dport, bitmask_t src_bm, bitmask_t dst_bm, payload_t *payload);

int packet_ip_to_buffer(abstract_packet_t *packet, unsigned char *buffer);

/* struct destroy functions */

void destroy_payload(payload_t *payload);

void destroy_abstract_packet(abstract_packet_t *packet);

/* print functions */

void print_payload(payload_t *payload);

void print_abstract_packet(abstract_packet_t *packet);