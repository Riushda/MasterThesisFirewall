import re

MQTT_PORT = 1883
MQTT_PUBLISH = 48

pattern = re.compile('\??([\w.]+)[=]?([\w.]+)?&?', re.IGNORECASE) # \??(\w+)=(\w+)&? # \??(\w+)[=]?(\w+)?&?

def decode_packet(dport, app_layer):
	if dport==MQTT_PORT : # if MQTT
		return decode_mqtt(app_layer)

# MQTT layer 
# Remark : msg_len is the length of the remaining fields (not counting itself)
#  _______________________________________________________________________________________
# |        |         |           |                   |                                    |
# | header | msg_len | topic_len |      topic        |              payload               |                                   
# | 1 byte | 1 byte  |  2 bytes  | topic_len byte(s) |  (msg_len - 2 - topic_len) byte(s) |                                                            
# |________|_________|___________|___________________|____________________________________|
#
		
def decode_mqtt(app_layer):

	if app_layer[0]==MQTT_PUBLISH :

		msg_len : int = app_layer[1]
		topic_len : int = int.from_bytes(app_layer[2:4], byteorder='big')

		offset = 4

		topic = app_layer[offset:offset+topic_len].decode("utf-8")
		offset += topic_len

		payload_len = msg_len - 2 - topic_len
		payload = app_layer[offset:offset+payload_len].decode("utf-8")

		groups = pattern.findall(payload)
		
		for i in range(len(groups)) : 
			if len(groups[i])>1 and groups[i][1]=="":
				groups[i] = groups[i][:-1] # pop second element if only value

		return [topic, groups]

	return None

		
