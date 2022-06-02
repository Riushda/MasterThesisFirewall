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

    """                            latency (ms)  |  queue size
        results : 0.01 (100)        0.756        |   0.184 
                  0.005 (200)       0.858        |   0.574  
                  0.004 (250)       0.878        |   0.681
                  0.002 (500)       1.493        |   4.831
                  0.001 (1000)      2.323        |   65.158
                  0.0005 (2000)     6.414        |   1534.160
    """

if __name__ == "__main__":
    # burst_measurements()
    throughput_measurements()