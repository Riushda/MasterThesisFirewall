import time

import paho.mqtt.client as mqtt

from constant import *

total = 0
count = 0


def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    # print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    # print(time.time_ns() - int(msg.payload))
    global total, count
    total += round(time.time() * 1000) - int(msg.payload)
    count += 1
    if count == MAX_COUNT:
        print(total / MAX_COUNT)
        count = 0
        total = 0


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))
    pass


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# mqttc.on_log = on_log

mqttc.connect(BROKER_IP, PORT)
mqttc.subscribe("bench")
mqttc.loop_forever()
