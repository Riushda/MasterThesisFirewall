class Member:
    def __init__(self, ip: str = None, port: int = None, field=None):
        self.ip = ip
        self.port = port
        if field is None:
            self.field = {}
        else:
            self.field = field

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
        if self.field:
            for field, content in self.field.items():
                result += f"{content}"
        else:
            result += "none"

        return result
