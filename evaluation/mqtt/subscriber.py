import time

import paho.mqtt.client as mqtt

from constant import *

total = 0
count = 0


def on_connect(mqttc, obj, flags, rc):
    print("Connected!")


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed!")


def on_message(mqttc, obj, msg):
    global total, count
    timing = int(str(msg.payload).split("=")[1][:-1])
    total += time.time_ns() - timing
    count += 1


if __name__ == "__main__":
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_subscribe = on_subscribe

    mqttc.connect(BROKER_IP, PORT)
    mqttc.subscribe("bench")
    mqttc.loop_start()
    time.sleep(WAITING_TIME)
    mqttc.loop_stop()

    if count != 0:
        print("Message count: " + str(count) + " message(s)")
        print("Average time: " + str(total / (count * 1000000)) + " ms")
    else:
        print("Zero count!")
