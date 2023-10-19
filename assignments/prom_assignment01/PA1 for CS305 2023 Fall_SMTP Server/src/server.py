from __future__ import annotations

from argparse import ArgumentParser
# from email.mime.text import MIMEText
from queue import Queue
import socket
from socketserver import ThreadingTCPServer, BaseRequestHandler
from threading import Thread

import tomli


def student_id() -> int:
    return 12111519  # TODO: replace with your SID


parser = ArgumentParser()
parser.add_argument('--name', '-n', type=str, required=True)
parser.add_argument('--smtp', '-s', type=int)
parser.add_argument('--pop', '-p', type=int)

args = parser.parse_args()

with open('data/config.toml', 'rb') as f:
    _config = tomli.load(f)
    SMTP_PORT = args.smtp or int(_config['server'][args.name]['smtp'])
    POP_PORT = args.pop or int(_config['server'][args.name]['pop'])
    ACCOUNTS = _config['accounts'][args.name]
    MAILBOXES = {account: [] for account in ACCOUNTS.keys()}

with open('data/fdns.toml', 'rb') as f:
    FDNS = tomli.load(f)

ThreadingTCPServer.allow_reuse_address = True


def fdns_query(domain: str, type_: str) -> str | None:
    domain = domain.rstrip('.') + '.'
    return FDNS[type_][domain]


class POP3Server(BaseRequestHandler):
    def handle(self):
        conn = self.request
        # establish connection
        # allow the connection on self defined port

        # get user
        user = conn.recv(1024).decode().split(' ')[1]
        if user not in ACCOUNTS:
            conn.sendall(b'-ERR no such user\r\n')
            return
        conn.sendall(b'+OK\r\n')
        # get password
        password = conn.recv(1024).decode().split(' ')[1]
        if password != ACCOUNTS[user]:
            conn.sendall(b'-ERR invalid password\r\n')
            return
        conn.sendall(b'+OK\r\n')
        # get command
        while True:
            command = conn.recv(1024).decode()
            if command.startswith('STAT'):
                conn.sendall(b'+OK 0 0\r\n')
            elif command.startswith('LIST'):
                conn.sendall(b'+OK 0 messages\r\n.\r\n')
            elif command.startswith('RETR'):
                conn.sendall(b'-ERR no such message\r\n')
            elif command.startswith('DELE'):
                conn.sendall(b'-ERR no such message\r\n')
            elif command.startswith('QUIT'):
                conn.sendall(b'+OK\r\n')
                break
            else:
                conn.sendall(b'-ERR invalid command\r\n')


class SMTPServer(BaseRequestHandler):
    def handle(self):
        conn = self.request
        ...


if __name__ == '__main__':
    if student_id() % 10000 == 0:
        raise ValueError('Invalid student ID')

    smtp_server = ThreadingTCPServer(('', SMTP_PORT), SMTPServer)
    pop_server = ThreadingTCPServer(('', POP_PORT), POP3Server)
    Thread(target=smtp_server.serve_forever).start()
    Thread(target=pop_server.serve_forever).start()
