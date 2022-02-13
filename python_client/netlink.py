import socket
from constant import *


class Netlink():

    def __init__(self):
        self.sock = socket.socket(
            socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_USERSOCK)
        self.sock.bind((0, 0))

    def close(self):
        self.sock.close()

    def send_msg(self, code, data):
        try:
            print(code.to_bytes(1, 'little') + data)
            self.sock.send(code.to_bytes(1, 'little') + data)
        except(socket.error):
            print("Error: netlink send")

    def recv_msg(self):
        try:
            self.sock.recv(MAX_PAYLOAD)
        except(socket.error):
            print("Error: netlink receive")
