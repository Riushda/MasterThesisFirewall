#include "protocol.h"

/* this function will fill packet and buffer, packet is used for matching and buffer sent to userspace */
int parse_packet(char *data, uint16_t port, abstract_packet_t *packet, char *buffer){
	
	if(port==MQTT_PORT){
		return parse_mqtt(data, packet, buffer);
	}

	return 0;
}

/*

MQTT layer 
Remark : msg_len is the length of the remaining fields (not counting itself)
________________________________________________________________________________________
|        |         |           |                   |                                    |
| header | msg_len | topic_len |      topic        |              payload               |                                   
| 1 byte | 1 byte  |  2 bytes  | topic_len byte(s) |  (msg_len - 2 - topic_len) byte(s) |                                                            
|________|_________|___________|___________________|____________________________________|

*/
int parse_mqtt(char *data, abstract_packet_t *packet, char *buffer){

	uint8_t application_header; 
    uint8_t msg_len;
    uint16_t topic_len;
    uint8_t payload_len;
    uint8_t topic_len_short;

    int offset;
	int parsed_len;

    format_t *pattern;
    content_t *content;
    data_t *p;

    parsed_len = 0;

	application_header = *(data);
    offset = 1;

    if(application_header==MQTT_PUBLISH){
        
        msg_len = *(data+offset);
        offset += 1;

        memcpy(&topic_len, data+offset, 2);
        topic_len = ntohs(topic_len);
        offset += 2;

        char topic[topic_len+1];
        memset(topic, 0, topic_len+1);
        memcpy(topic, data+offset, topic_len);

        offset += topic_len;

        payload_len = msg_len - 2 - topic_len; 
        char payload[payload_len+1];
        memset(payload, 0, payload_len+1);
        memcpy(payload, data+offset, payload_len);

        parsed_len = 1 + topic_len + 1 + payload_len;

        printk(KERN_INFO "topic : %s\n", topic);
        printk(KERN_INFO "payload : %s\n", payload);

        // choose the pattern of payload, hardcoded for now

        // match \??(\w+)=(\w+)&? => regex to keep if needed later

        pattern = NULL;
        create_format(&pattern, 1, "=", "&", NULL); // match ?field1=value1&field2=value2&....
        //create_format(&pattern, 1, ":", ",", "}"); // match json {field1: value1, field2: value2, ... }

        // set informations in packet (for rule matching)

        p = NULL;
        
        decode_payload(pattern, payload, payload_len, &p); // fix crash when payload doesn't match, strsep tests in kernel_tests

        create_content(&content, STRING_TYPE, topic_len, topic, p);

        packet->content = content;

        destroy_format(pattern);

        // concatenate informations in buffer (for userspace)

        topic_len_short = (uint8_t) topic_len;

        memset(buffer, 0, parsed_len);

        memcpy(buffer + offset, &topic_len_short, 1);
        offset += 1;
        memcpy(buffer + offset, topic, topic_len);
        offset += topic_len;
        memcpy(buffer + offset, &payload_len, 1);
        offset += 1;
        memcpy(buffer + offset, payload, payload_len);
    }
	else{
		return -1; // not a publish message
	}

	return parsed_len;
}