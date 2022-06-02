import asyncio
import time
import logging

from aiocoap import *

MESSAGE_COUNT = 10000
INTERVAL_TIME = 0.000555556

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
        global total, count, samples
        count += 1
        timing = int(str(response.payload).split("=")[1][:-1])
        sample = time.time_ns() - timing
        total += sample
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


def throughput_measurements():
    global total, count
    asyncio.set_event_loop(asyncio.new_event_loop())

    asyncio.get_event_loop().run_until_complete(create_tasks_func())

    average = total / (count * 1000000)
    print("Message count: " + str(count) + " message(s)")
    print("Average latency: " + str(average) + " ms")


if __name__ == "__main__":
    # burst_measurements()
    throughput_measurements()
