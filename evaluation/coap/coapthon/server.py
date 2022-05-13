from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource


class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port))
        self.add_resource('basic/test', BasicResource(coap_server=self))


class BasicResource(Resource):
    def __init__(self, name="BasicResource", coap_server=None):
        super(BasicResource, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = "Basic Resource"
        self.server = coap_server

    def render_GET(self, request):
        print(request)
        return self

    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_POST(self, request):
        res = BasicResource()
        res.location_query = request.uri_query
        res.payload = request.payload

        #server: CoAPServer = self._coap_server
        #server.notify(self.name)
        print(self.name)
        return res

    def render_DELETE(self, request):
        return True


def main():
    server = CoAPServer("192.168.33.12", 5683)
    try:
        server.listen(10)
    except KeyboardInterrupt:
        print("Server Shutdown")
        server.close()
        print("Exiting...")


if __name__ == '__main__':
    main()