#include "../rule/rule.h"

#define MQTT_PUBLISH 48
#define MQTT_PORT 1883 // encrypted mqtt port : 8883
#define MAX_PACKET_SIZE 1024

int parse_packet(char * packet, uint16_t port, char *buff);

int parse_mqtt(char *packet, char *buff);