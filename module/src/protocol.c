#include "protocol.h"

int parse_packet(char * packet, uint16_t port, char *buffer){
	
	if(port==MQTT_PORT){
		return parse_mqtt(packet, buffer);
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
int parse_mqtt(char *packet, char *buffer){

	uint8_t application_header;
    int offset; 
    uint8_t msg_len;
    uint16_t topic_len;
    uint8_t payload_len;
    uint8_t topic_len_short;
	int buffer_len = 0;

	application_header = *(packet);

    if(application_header==MQTT_PUBLISH){
        msg_len = *(packet+1);

        memcpy(&topic_len, packet+2, 2);
        topic_len = ntohs(topic_len);

        offset = 4;

        char topic[topic_len+1];
        memset(topic, 0, topic_len+1);
        memcpy(topic, packet+offset, topic_len);

        offset += topic_len;

        payload_len = msg_len - 2 - topic_len; 
        char payload[payload_len+1];
        memset(payload, 0, payload_len+1);
        memcpy(payload, packet+offset, payload_len);

        printk(KERN_INFO "topic : %s\n", topic);
        printk(KERN_INFO "payload : %s\n", payload);

        // concatenate informations

        topic_len_short = (uint8_t) topic_len;
        
        buffer_len = 12 + 1 + topic_len + 1 + payload_len;

        offset = 12; // sizeof(rule_t) set by rule_to_buffer in firewall.c

        memcpy(buffer + offset, &topic_len_short, 1);
        offset += 1;
        memcpy(buffer + offset, topic, topic_len);
        offset += topic_len;
        memcpy(buffer + offset, &payload_len, 1);
        offset += 1;
        memcpy(buffer + offset, payload, payload_len);
    }
	else{
		return 0; // not a publish message
	}

	return buffer_len;
}