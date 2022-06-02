import asyncio
import csv
import time
import logging

from aiocoap import *

MESSAGE_COUNT = 10000
INTERVAL_TIME = 0.0005
NB_TRY = 10
LOOP_WAIT = 1

total = 0
count = 0

# logging setup
logging.basicConfig(level=logging.disable())
logging.getLogger("coap-server").setLevel(logging.DEBUG)


async def send(duration):
    protocol = await Context.create_client_context()
    request = Message(code=Code.GET, uri='coap://192.168.33.12/bench')
    try:
        await asyncio.sleep(duration)
        response = await protocol.request(request).response
        global total, count
        count += 1
        timing = int(str(response.payload).split("=")[1][:-1])
        total += time.time_ns() - timing
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)


async def create_tasks_func():
    input_coroutines = list()
    total_duration = 0
    for i in range(MESSAGE_COUNT):
        input_coroutines.append(send(total_duration))
        total_duration += INTERVAL_TIME
    res = await asyncio.gather(*input_coroutines, return_exceptions=False)
    return res


def burst_measurements():
    global total, count
    asyncio.set_event_loop(asyncio.new_event_loop())
    total_average = 0
    for i in range(NB_TRY):
        asyncio.get_event_loop().run_until_complete(create_tasks_func())
        if count != 0:
            current_average = total / (count * 1000000)
            print("Message count: " + str(count) + " message(s)")
            print("Average time: " + str(current_average) + " ms")
        total_average += current_average
        count = 0
        total = 0
        time.sleep(LOOP_WAIT)
    total_average /= NB_TRY
    print("Average 10 tries: " + str(total_average) + " ms")


def throughput_measurements():
    global total, count
    asyncio.set_event_loop(asyncio.new_event_loop())

    asyncio.get_event_loop().run_until_complete(create_tasks_func())

    average = total / (count * 1000000)
    print("Message count: " + str(count) + " message(s)")
    print("Average latency: " + str(average) + " ms")

    """                            latency (ms)  |  queue size
        results : 0.01 (100)        7.426        |   0.283
                  0.005 (200)       15.627       |   1.023            
                  0.004 (250)       33.244       |   20.363
                  0.002 (500)       5732.803     |   151.648
                  0.001 (1000)      5105.861     |   206.242
                  0.0005 (2000)     5785.709     |   317.484
    """


if __name__ == "__main__":
    # burst_measurements()
    throughput_measurements()



