import logging
import asyncio

from aiocoap import *

logging.basicConfig(level=logging.INFO)


async def main():
    protocol = await Context.create_client_context()

    request = Message(code=Code.GET, uri='coap://192.168.33.12/time')
    try:
        #response = await protocol.request(request).response
        response = await protocol.request(request).observation
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        print('Result: %s\n%r' % (response.code, response.payload))

    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    asyncio.run(main())
