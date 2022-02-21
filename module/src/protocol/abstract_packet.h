#include "../constraints/data_constraint.h"

typedef struct content
{
	enum data_type type;
	uint8_t subject_len;
	char *subject;
	data_t *payload;
} content_t;

typedef struct abstract_packet
{
	int src;
    int dst;
    short sport;
    short dport;
	bitmask_t src_bm;
    bitmask_t dst_bm;
	content_t *content;
} abstract_packet_t;

/* match constraint function */

int match_data_constraint(content_t *content, data_constraint_t *data_c, int rule_index);

/* create struct functions */

int create_content(content_t **content, uint8_t type, uint8_t subject_len, char *subject, data_t *payload);

int create_abstract_packet(abstract_packet_t *packet, int src, int dst, short sport, short dport, bitmask_t src_bm, bitmask_t dst_bm, content_t *content);

int packet_ip_to_buffer(abstract_packet_t *packet, unsigned char *buffer);

/* struct destroy functions */

void destroy_content(content_t *content);

void destroy_abstract_packet(abstract_packet_t *packet);

/* print functions */

void print_content(content_t *content);

void print_abstract_packet(abstract_packet_t *packet);