from coapthon.client.helperclient import HelperClient

host = "192.168.33.12"
port = 5683
path = "basic/test?name=hello"

client = HelperClient(server=(host, port))
#response = client.get(path)
response = client.observe(path, print("resource changed"), Timeout=20)
print(response.pretty_print())
#client.post(path, "hello")
client.stop()