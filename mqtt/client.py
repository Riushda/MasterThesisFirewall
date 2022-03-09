import paho.mqtt.client as mqtt #import the client1
'''
broker_address="192.168.1.4"
port=8883
#broker_address="iot.eclipse.org" #use external broker
client = mqtt.Client("P1") #create new instance
client.tls_set('./certs/ca.crt', tls_version=2)
#client.tls_insecure_set(True)
client.connect(broker_address, port) #connect to broker
client.publish("house/main-light","OFF")#publish
client.disconnect()
'''

broker_address="192.168.1.230"
port=1883

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("hello")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client("P1") #create new instance
client.connect(broker_address, port) #connect to broker

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
