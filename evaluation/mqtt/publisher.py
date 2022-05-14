import time

import paho.mqtt.client as mqtt

from constant import *


def sleep(duration, get_now=time.perf_counter):
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()


def on_publish(mqttc, obj, mid):
    pass


if __name__ == "__main__":
    mqttc = mqtt.Client()
    mqttc.on_publish = on_publish
    mqttc.connect(BROKER_IP, PORT)

    for i in range(MESSAGE_COUNT):
        mqttc.publish("bench", "?timing=" + str(time.time_ns()))
        sleep(INTERVAL_TIME)