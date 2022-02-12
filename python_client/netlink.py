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
            message = code.to_bytes(1, 'little') + data
            length = 4 * len(message)
            print(length.to_bytes(2, 'little') + message)
            self.sock.send(length.to_bytes(2, 'little') + message)
        except(socket.error):
            print("Error while sending")

    def recv_msg(self):
        try:
            self.sock.recv(MAX_PAYLOAD)
        except(socket.error):
            print("Error while receiving")
