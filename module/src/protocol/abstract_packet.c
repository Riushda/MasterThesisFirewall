#include "abstract_packet.h"

/* create struct functions */

int create_payload(payload_t **payload, uint8_t type, uint8_t field_len, char *field, data_t *data){
	
	*payload = (payload_t *)kmalloc(sizeof(payload_t), GFP_KERNEL);
	if(*payload==NULL)
		return -1;

	memset(*payload, 0, sizeof(payload_t));

	(*payload)->type = type;
	(*payload)->field_len = field_len;

	(*payload)->field = (char *)kmalloc(field_len, GFP_KERNEL);
	if((*payload)->field==NULL){
		return -1;
	}

	memset((*payload)->field, 0, field_len);
	memcpy((*payload)->field, field, field_len);

	(*payload)->data = data;

	return 0;
}

int create_abstract_packet(abstract_packet_t *packet, int src, int dst, short sport, short dport, bitmask_t src_bm, bitmask_t dst_bm, payload_t *payload){

	memset(packet, 0, sizeof(abstract_packet_t));

	memcpy(&packet->src, &src, sizeof(int));
    memcpy(&packet->src_bm, &src_bm, 1);
    memcpy(&packet->dst, &dst, sizeof(int));
    memcpy(&packet->dst_bm, &dst_bm, 1);

	memcpy(&packet->sport, &sport, sizeof(short));
    memcpy(&packet->dport, &dport, sizeof(short));

	packet->payload = payload;

	return 0;
}

int packet_ip_to_buffer(abstract_packet_t *packet, unsigned char *buffer)
{
    int offset;
    offset = 0;

    memcpy(buffer + offset, &packet->src, sizeof(packet->src));
    offset += sizeof(packet->src);
    memcpy(buffer + offset, &packet->dst, sizeof(packet->dst));
    offset += sizeof(packet->dst);
    memcpy(buffer + offset, &packet->sport, sizeof(packet->sport));
    offset += sizeof(packet->sport);
    memcpy(buffer + offset, &packet->dport, sizeof(packet->dport));
    offset += sizeof(packet->dport);

    return offset;
}

/* struct destroy functions */

void destroy_payload(payload_t *payload){

	if(payload==NULL)
		return;

	if(payload->field!=NULL)
		kfree(payload->field);
	
	if(payload->data!=NULL)
		destroy_data_t(payload->data, payload->type);

	kfree(payload);
}

void destroy_abstract_packet(abstract_packet_t *packet){
	destroy_payload(packet->payload);
	return;
}

/* print functions */

void print_payload(payload_t *payload){
	if(payload!=NULL){
		printk(KERN_INFO "payload : ");
		printk(KERN_CONT "type : %d ", payload->type);
		printk(KERN_CONT "field_len : %d ", payload->field_len);
		printk(KERN_CONT "field : %s\n", payload->field);

		print_data_t(payload->data, payload->type);
	}
}

void print_abstract_packet(abstract_packet_t *packet){

	printk(KERN_INFO "packet : ");

	printk(KERN_CONT "Src: %pI4/%d ", &packet->src, packet->src_bm);
	printk(KERN_CONT "Dst: %pI4/%d ", &packet->dst, packet->dst_bm);

	printk(KERN_CONT "Sport: %d ", ntohs(packet->sport));
	printk(KERN_CONT "Dport: %d\n ", ntohs(packet->dport));

	print_payload(packet->payload);
	return;
}