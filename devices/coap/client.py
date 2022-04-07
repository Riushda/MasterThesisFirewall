from coapthon.client.helperclient import HelperClient

host = "192.168.33.12"
port = 5683
path = "basic/test?name=hello"

client = HelperClient(server=(host, port))
response = client.get(path)
print(response.pretty_print())
client.stop()
