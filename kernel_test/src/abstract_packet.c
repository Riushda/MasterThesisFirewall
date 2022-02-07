#include "abstract_packet.h"

/* create struct functions */

int create_payload(payload_t **payload, uint8_t type, uint8_t field_len, char *field, data_t *data){

	if(*payload!=NULL)
		return -1;

	*payload = (payload_t *)malloc(sizeof(payload_t));
	if(*payload==NULL)
		return -1;
	
	memset(*payload, 0, sizeof(payload_t));

	(*payload)->type = type;
	(*payload)->field_len = field_len;

	(*payload)->field = (char *)malloc(field_len);
	if((*payload)->field==NULL){
		free(*payload);
		return -1;
	}

	memset((*payload)->field, 0, field_len);
	memcpy((*payload)->field, field, field_len);

	(*payload)->data = data;

	return 0;
}

int create_abstract_packet(abstract_packet_t **packet, rule_t rule, payload_t *payload){

	*packet = (abstract_packet_t *)malloc(sizeof(abstract_packet_t));
	if(*packet==NULL)
		return -1;

	memset(&((*packet)->rule), 0, sizeof(rule_t));
	memcpy(&((*packet)->rule), &rule, sizeof(rule_t));

	(*packet)->payload = payload;

	return 0;
}

/* struct destroy functions */

void destroy_payload(payload_t *payload){

	if(payload==NULL)
		return;

	if(payload->field!=NULL)
		free(payload->field);
	
	if(payload->data!=NULL)
		destroy_data_t(payload->data, payload->type);
	
	free(payload);
}

void destroy_abstract_packet(abstract_packet_t *packet){
	destroy_payload(packet->payload);
	free(packet);
	return;
}

/* print functions */

void print_payload(payload_t *payload){
	printf( "payload :\n");
	printf( " 	type : %d\n", payload->type);
	printf( " 	field_len : %d\n", payload->field_len);
	printf( " 	field : %s\n", payload->field);

	print_data_t(payload->data, payload->type);
}

void print_abstract_packet(abstract_packet_t *packet){
	print_rule(packet->rule);
	print_payload(packet->payload);
	return;
}