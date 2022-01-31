import rule


class Relation():
    def __init__(self, first: rule, second: rule = None):
        self.first = first
        self.second = second

    def __str__(self):
        if(self.second):
            return f"{self.first} ~ {self.second}"
        else:
            return f"{self.first}"

