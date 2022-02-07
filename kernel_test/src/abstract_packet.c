#include "abstract_packet.h"

/* convert buffer to struct functions */

int buffer_to_payload(char *buf, payload_t **payload){
	return 0;
}

int buffer_to_abstract_packet(char *buf, abstract_packet_t **packet){
	return 0;
}

/* convert struct to buffer functions */

int payload_to_buffer(payload_t *payload, char **buf){
	return 0;
}

int abstract_packet_to_buffer(abstract_packet_t *packet, char **buf){
	return 0;
}

/* create struct functions */

int create_payload(payload_t **payload, uint8_t type, uint8_t field_len, char *field, data_t *data){
	return 0;
}

int create_abstract_packet(abstract_packet_t **packet, int src, int dst, short sport, short dport, payload_t *payload){
	return 0;
}

/* struct destroy functions */

void destroy_payload(payload_t *payload){
	return;
}

void destroy_abstract_packet(abstract_packet_t *packet){
	return;
}

/* print functions */

void print_payload(data_t *data, uint8_t type){
	return;
}

void print_abstract_packet(abstract_packet_t *packet){
	return;
}