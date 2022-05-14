import time
import logging

import asyncio

import aiocoap.resource as resource
import aiocoap


class BenchResource(resource.Resource):
    def __init__(self):
        super().__init__()

    async def render_get(self, request):
        payload = f"?timing={str(time.time_ns())}".encode('ascii')
        return aiocoap.Message(payload=payload)


# logging setup
logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)


async def main():
    # Resource tree creation
    root = resource.Site()

    root.add_resource(['.well-known', 'core'],
                      resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(['bench'], BenchResource())
    await aiocoap.Context.create_server_context(root)

    # Run forever
    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())
