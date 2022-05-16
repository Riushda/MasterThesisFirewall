import csv
import time

import paho.mqtt.client as mqtt

from constant import *

total = 0
count = 0
total_average = 0
row_index = 0

f = open('plot/output.csv', 'w', encoding='UTF8')
writer = csv.writer(f)


def sleep(duration, get_now=time.perf_counter):
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()


def on_message(mqttc, obj, msg):
    global total, count, total_average, row_index
    timing = int(str(msg.payload).split("=")[1][:-1])
    total += time.time_ns() - timing
    # print((time.time_ns() - timing) / 1000000)
    count += 1
    if count == MESSAGE_COUNT:
        current_average = total / (MESSAGE_COUNT * 1000000)
        total_average += current_average
        print("Message count: " + str(count) + " message(s)")
        print("Average time: " + str(current_average) + " ms")
        current_row = [row_index, current_average]
        writer.writerow(current_row)
        total = 0
        count = 0
        row_index += 1


def on_connect(mqttc, obj, flags, rc):
    print("Connected!")


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed!")


def main():
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_subscribe = on_subscribe

    mqttc.connect(BROKER_IP, PORT)
    mqttc.subscribe("bench")
    mqttc.loop_start()
    time.sleep(WAITING_TIME)
    mqttc.loop_stop()
    global total_average
    total_average /= NB_TRY
    row = ["mean", total_average]
    writer.writerow(row)
    print("Average 10 tries: " + str(total_average) + " ms")


if __name__ == "__main__":
    main()
