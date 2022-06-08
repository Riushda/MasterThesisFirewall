import time

import paho.mqtt.client as mqtt

from constant import *


def sleep(duration, get_now=time.perf_counter):
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()


def burst_measurements():
    mqttc = mqtt.Client()
    mqttc.connect(BROKER_IP, PORT)

    for j in range(NB_TRY):
        for i in range(MESSAGE_COUNT):
            mqttc.publish("bench", "?timing=" + str(time.time_ns()))
            sleep(INTERVAL_TIME)
        sleep(LOOP_WAIT)


def throughput_measurements():
    mqttc = mqtt.Client()
    mqttc.connect(BROKER_IP, PORT)

    for i in range(MESSAGE_COUNT):
        mqttc.publish("bench", "?timing=" + str(time.time_ns()))
        sleep(INTERVAL_TIME)


if __name__ == "__main__":
    # burst_measurements()
    throughput_measurements()
