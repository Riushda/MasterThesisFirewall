import socket
from constant import *


class Netlink():

    def __init__(self):
        self.sock = socket.socket(
            socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_USERSOCK)
        self.sock.bind((0, 0))

    def close(self):
        self.sock.close()

    def send_msg(self, data):
        try:
            self.sock.send(data)
        except(socket.error):
            print("Error while sending")

    def recv_msg(self):
        try:
            self.sock.recv(MAX_PAYLOAD)
        except(socket.error):
            print("Error while receiving")
