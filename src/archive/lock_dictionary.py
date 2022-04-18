import threading


class LockDictionary:
    def __init__(self):
        self.dict = {}
        self.lock = threading.Lock()

    def set(self, key, value):
        with self.lock:
            self.dict[key] = value

    def delete(self, key):
        with self.lock:
            del self.dict[key]

    def get(self, key):
        with self.lock:
            return self.dict[key]
