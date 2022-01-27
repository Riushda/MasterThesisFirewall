import paho.mqtt.client as mqtt #import the client1
broker_address="192.168.1.4"
port=8883
#broker_address="iot.eclipse.org" #use external broker
client = mqtt.Client("P1") #create new instance
client.tls_set('./certs/ca.crt', tls_version=2)
#client.tls_insecure_set(True)
client.connect(broker_address, port) #connect to broker
client.publish("house/main-light","OFF")#publish
client.disconnect()