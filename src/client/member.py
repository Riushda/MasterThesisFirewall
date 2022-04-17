class Member:
    def __init__(self, ip: str = None, port: int = None, fields=None, is_ip6: bool = False):
        self.ip = ip
        self.is_ip6 = is_ip6
        self.port = port
        if fields is None:
            self.fields = {}
        else:
            self.fields = fields

    def __str__(self):
        result = "source: "

        if self.ip:
            result += self.ip + ":"
        else:
            result += "*:"

        if self.port:
            result += str(self.port)
        else:
            result += "*"

        result += " | fields: "
        if self.fields:
            for field, content in self.fields.items():
                result += f"{content}"
        else:
            result += "none"

        return result
