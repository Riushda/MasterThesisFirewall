import asyncio
import random
import time

from constant import *
from aiocoap import *

total = 0
count = 0


# logging.basicConfig(level=logging.INFO)


async def send(duration):
    await asyncio.sleep(duration)
    protocol = await Context.create_client_context()
    request = Message(code=Code.GET, uri='coap://192.168.33.12/bench')
    try:
        response = await protocol.request(request).response
        global total, count
        count += 1
        timing = int(str(response.payload).split("=")[1][:-1])
        total += time.time_ns() - timing
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        pass
        # print('Result: %s\n%r' % (response.code, response.payload))


def sleep(duration, get_now=time.perf_counter):
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()


async def create_tasks_func():
    tasks = list()
    total_duration = 0
    for i in range(MESSAGE_COUNT):
        tasks.append(asyncio.create_task(send(total_duration)))
        total_duration += INTERVAL_TIME
    await asyncio.wait(tasks)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(create_tasks_func())
    if count != 0:
        print("Message count: " + str(count) + " message(s)")
        print("Average time: " + str(total / (count * 1000000)) + " ms")
    else:
        print("Zero count!")
