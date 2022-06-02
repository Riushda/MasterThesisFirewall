import time

import paho.mqtt.client as mqtt

from constant import *

total = 0
count = 0
total_average = 0


def on_message(mqttc, obj, msg):
    global total, count, total_average
    timing = int(str(msg.payload).split("=")[1][:-1])
    sample = time.time_ns() - timing
    total += sample
    count += 1
    # if count == MESSAGE_COUNT:
    if count == 50000:
        current_average = total / (MESSAGE_COUNT * 1000000)
        total_average += current_average
        print("Message count: " + str(count) + " message(s)")
        print("Average time: " + str(current_average) + " ms")


def on_connect(mqttc, obj, flags, rc):
    print("Connected!")


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed!")


def main():
    global mqttc
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_subscribe = on_subscribe
    mqttc.connect(BROKER_IP, PORT)
    mqttc.subscribe("bench")
    mqttc.loop_forever(timeout=30)


if __name__ == "__main__":
    main()