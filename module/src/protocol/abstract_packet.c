#include "abstract_packet.h"

/*int decode_payload(char *buf, data_t **payload){
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
}*/

/* return 0 if at least one data_t of the constraint match the payload */

int match_payload(content_t *content, data_constraint_t *data_c){
	int condition;
	int match_type;
	int match_field;

	int data_str_len;

	data_t *constraint;
	data_t *curr_data;

	constraint = data_c->data;
	curr_data = content->payload;
	while(curr_data!=NULL){

		condition = 0;

		while(constraint!=NULL){

			match_type = data_c->type==curr_data->type || (data_c->type==INT_RANGE_TYPE && curr_data->type==INT_TYPE);

			if(match_type){

				if(curr_data->field==NULL){ // if data has not field, then subject is considered to be its field
					match_field = content->subject_len==data_c->field_len;
					if(match_field)
						match_field = !memcmp(content->subject, data_c->field, data_c->field_len);
				}
				else{
					match_field = curr_data->field_len==data_c->field_len;
					if(match_field)
						match_field = !memcmp(curr_data->field, data_c->field, curr_data->field_len);
				}

				if(match_field){

					switch (data_c->type)
					{
						case INT_TYPE:
							condition = (constraint->value).int_value != (curr_data->value).int_value;
							break;
						case STRING_TYPE:
							data_str_len = (curr_data->value).str_value.str_len;
							condition = (constraint->value).str_value.str_len != data_str_len;
							if(!condition)
								condition = memcmp((constraint->value).str_value.str, (curr_data->value).str_value.str, data_str_len);
							break;
						case INT_RANGE_TYPE:
							condition = (constraint->value).int_range.start <= (curr_data->value).int_value;
							condition += (constraint->value).int_range.end >= (curr_data->value).int_value;
							break;
						default:
							break;
					}

					if(!condition) // if constraint matching current payload data found
						break;
				}

			}

			constraint = constraint->next;

		}

		if(condition) // if at least one constraint matches payload data field but not value
			break;

		curr_data = curr_data->next;
	}

	return condition;
}

/* check if all the constraints of the rule of index rule_index match the packet content 
*  return 0 if success
*/

int match_data_constraint(content_t *content, data_constraint_t *data_c, int rule_index){

	int condition;

	data_constraint_t *element;
	element = data_c;
	while(element!=NULL){

		condition = 0;

		if(is_set_v(element->vector, rule_index)){ // check if rule is constrained by the current constraint 

			switch (element->type)
			{
				case SUBJECT_TYPE:
					condition = element->field_len!=content->subject_len;
					if(!condition)
						condition = memcmp(element->field, content->subject, content->subject_len);
					break;
				default:
					condition = match_payload(content, element);
					break;
			}
			
		}

		if(condition)
			break;

		element = element->next;
	}

	return condition;
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
	short port;
    offset = 0;

    memcpy(buffer + offset, &packet->src, sizeof(packet->src));
    offset += sizeof(packet->src);
    memcpy(buffer + offset, &packet->dst, sizeof(packet->dst));
    offset += sizeof(packet->dst);

	port = htons(packet->sport);
    memcpy(buffer + offset, &port, sizeof(packet->sport));
    offset += sizeof(packet->sport);

	port = htons(packet->dport);
    memcpy(buffer + offset, &port, sizeof(packet->dport));
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

		print_data_t(content->payload, content->type);
	}
}

void print_abstract_packet(abstract_packet_t *packet){
	int src;
	int dst;

	printk(KERN_INFO "packet : ");
	
	src = htonl(packet->src); 
	printk(KERN_CONT "Src: %pI4/%d ", &src, packet->src_bm);

	dst = htonl(packet->dst); 
	printk(KERN_CONT "Dst: %pI4/%d ", &dst, packet->dst_bm);

	printk(KERN_CONT "Sport: %d ", ntohs(packet->sport));
	printk(KERN_CONT "Dport: %d\n ", ntohs(packet->dport));

	print_content(packet->content);
	return;
}