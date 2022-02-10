#include "abstract_packet.h"

/* create struct functions */

int create_payload(payload_t **payload, uint8_t type, uint8_t field_len, char *field, data_t *data){

	*payload = (payload_t *)malloc(sizeof(payload_t));
	if(*payload==NULL)
		return -1;

	memset(*payload, 0, sizeof(payload_t));

	(*payload)->type = type;
	(*payload)->field_len = field_len;

	(*payload)->field = (char *)malloc(field_len);
	if((*payload)->field==NULL){
		return -1;
	}

	memset((*payload)->field, 0, field_len);
	memcpy((*payload)->field, field, field_len);

	(*payload)->data = data;

	return 0;
}

int create_abstract_packet(abstract_packet_t *packet, int src, int dst, int sport, int dport, bitmask_t src_bm, bitmask_t dst_bm, payload_t *payload){

	memset(packet, 0, sizeof(abstract_packet_t));

	packet->src = src;
	packet->dst = dst;
	packet->sport = sport;
	packet->dport = dport;
	packet->src_bm = src_bm;
	packet->dst_bm = dst_bm;

	packet->payload = payload;

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
	return;
}

/* print functions */

void print_payload(payload_t *payload){
	if(payload!=NULL){
		printf( "payload :\n");
		printf( " 	type : %d\n", payload->type);
		printf( " 	field_len : %d\n", payload->field_len);
		printf( " 	field : %s\n", payload->field);

		print_data_t(payload->data, payload->type);
	}
}

void print_abstract_packet(abstract_packet_t *packet){
	struct in_addr addr;
    int src;
    int dst;

	src = ntohl(packet->src);
    memcpy(&addr, &src, sizeof(struct in_addr));
	printf("Src: %s/%d\n", inet_ntoa(addr), packet->src_bm);

	dst = ntohl(packet->dst);
    memcpy(&addr, &dst, sizeof(struct in_addr));
	printf("Dst: %s/%d\n", inet_ntoa(addr), packet->dst_bm);

	printf("Sport: %d\n", ntohs(packet->sport));
	printf("Dport: %d\n", ntohs(packet->dport));

	print_payload(packet->payload);
	return;
}