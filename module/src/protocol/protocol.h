#include "../rule/rule.h"

#define MQTT_PUBLISH 48
#define MQTT_PORT 1883 // encrypted mqtt port : 8883
#define MAX_PACKET_SIZE 1024

int parse_packet(abstract_packet_t *packet, char *data, uint16_t port, char *buffer);

int parse_mqtt(abstract_packet_t *packet, char *data, char *buffer);