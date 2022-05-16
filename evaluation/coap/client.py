import asyncio
import csv
import time
import logging

from aiocoap import *

MESSAGE_COUNT = 1000
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


def main():
    global total, count
    asyncio.set_event_loop(asyncio.new_event_loop())
    with open('plot/output.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        total_average = 0
        for i in range(NB_TRY):
            asyncio.get_event_loop().run_until_complete(create_tasks_func())
            if count != 0:
                current_average = total / (count * 1000000)
                row = [i, current_average]
                writer.writerow(row)
                print("Message count: " + str(count) + " message(s)")
                print("Average time: " + str(current_average) + " ms")
            else:
                print("Zero count!")
            total_average += current_average
            count = 0
            total = 0
            time.sleep(LOOP_WAIT)
        total_average /= NB_TRY
        row = ["mean", total_average]
        writer.writerow(row)
        print("Average 10 tries: " + str(total_average) + " ms")


if __name__ == "__main__":
    main()

