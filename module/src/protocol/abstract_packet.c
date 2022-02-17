#include "abstract_packet.h"

int decode_payload(char *buf, data_t **payload){
	char *token;
	char *running = buf;
	const char delimiter[2] = "&";
	if(memcmp(buf, "?", 1))
		return -1;
	
	token = strsep(&running, delimiter);
	while(token){
		
		
		token = strsep(&running, delimiter);
	}

	return 0;
}

/* match packet with constraint */

data_constraint_t *match_data_constraint(abstract_packet_t *packet, data_constraint_t *data_c){

	int condition;

	data_constraint_t *element = data_c;
	while(element!=NULL){

		condition = element->type==type;
		if(condition){
			condition = element->field_len==field_len;
			if(condition){
				condition = memcmp(element->field, field, field_len);
				if(!condition){

					if(type==SUBJECT_TYPE)
						return element;

					condition = match_data_t(element->data, data, type);
					if(!condition)
						return element;
				}
			}
		}	

		element = element->next;
	}

	return NULL;
}

/* create struct functions */

int create_content(content_t **content, uint8_t type, uint8_t subject_len, char *subject, data_t *payload){
	
	*content = (content_t *)kmalloc(sizeof(content_t), GFP_KERNEL);
	if(*content==NULL)
		return -1;

	memset(*content, 0, sizeof(content_t));

	(*content)->type = type;
	(*content)->subject_len = subject_len;

	(*content)->subject = (char *)kmalloc(subject_len + 1, GFP_KERNEL);
	if((*content)->subject==NULL){
		return -1;
	}

	memset((*content)->subject, 0, subject_len + 1);
	memcpy((*content)->subject, subject, subject_len);

	(*content)->payload = payload;

	return 0;
}

int create_abstract_packet(abstract_packet_t *packet, int src, int dst, short sport, short dport, bitmask_t src_bm, bitmask_t dst_bm, content_t *content){

	memset(packet, 0, sizeof(abstract_packet_t));

	src = htonl(src);
	dst = htonl(dst);

	memcpy(&packet->src, &src, sizeof(int));
    memcpy(&packet->src_bm, &src_bm, 1);
    memcpy(&packet->dst, &dst, sizeof(int));
    memcpy(&packet->dst_bm, &dst_bm, 1);

	memcpy(&packet->sport, &sport, sizeof(short));
    memcpy(&packet->dport, &dport, sizeof(short));

	packet->content = content;

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

void destroy_content(content_t *content){

	if(content==NULL)
		return;

	if(content->subject!=NULL)
		kfree(content->subject);
	
	if(content->payload!=NULL)
		destroy_data_t(content->payload, content->type);

	kfree(content);
}

void destroy_abstract_packet(abstract_packet_t *packet){
	destroy_content(packet->content);
	return;
}

/* print functions */

void print_content(content_t *content){
	if(content!=NULL){
		printk(KERN_INFO "content : ");
		printk(KERN_CONT "type : %d ", content->type);
		printk(KERN_CONT "subject_len : %d ", content->subject_len);
		printk(KERN_CONT "subject : %s\n", content->subject);

		print_payload_t(content->payload, content->type);
	}
}

void print_abstract_packet(abstract_packet_t *packet){

	printk(KERN_INFO "packet : ");
	
	int src = htonl(packet->src); 
	printk(KERN_CONT "Src: %pI4/%d ", &src, packet->src_bm);

	int dst = htonl(packet->dst); 
	printk(KERN_CONT "Dst: %pI4/%d ", &dst, packet->dst_bm);

	printk(KERN_CONT "Sport: %d ", ntohs(packet->sport));
	printk(KERN_CONT "Dport: %d\n ", ntohs(packet->dport));

	print_content(packet->content);
	return;
}