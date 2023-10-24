from __future__ import annotations

from argparse import ArgumentParser
# from email.mime.text import MIMEText
from queue import Queue
import socket
from socketserver import ThreadingTCPServer, BaseRequestHandler
from threading import Thread

import tomli


def student_id() -> int:
    return 12111519


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


def print_message(message):
    print('receive message: ', end='')
    for word in message:
        print(f'\"{word}\",', end='')
    print(';')


def get_message(conn, to_print=False, no_decode=False, no_substr=False, no_split=False, to_print_ori=False, ):
    message = conn.recv(1024)
    if no_decode:
        if to_print:
            print(message.decode())
        return message
    message = message.decode()
    if no_substr:
        if to_print:
            print(message)
        return message
    message = message.rstrip('\r\n')
    if no_split:
        if to_print:
            print(message)
        return message
    if to_print_ori and to_print:
        print(message)
    message = message.split(' ')
    if to_print:
        print_message(message)
    return message


# error report for POP3
CONN_REFUSED = 0
AUTH_FAILED = 1
INVALID_COMMAND = 2
INVALID_ARGUMENT = 3


def pop_error_report(error_code, msg=None):
    error_msg = ''
    if error_code == CONN_REFUSED:
        error_msg = '-ERR Connection refused'
    elif error_code == AUTH_FAILED:
        error_msg = '-ERR Authentication failed'
    elif error_code == INVALID_COMMAND:
        error_msg = '-ERR Invalid command'
    elif error_code == INVALID_ARGUMENT:
        error_msg = '-ERR Invalid argument'
    else:
        error_msg = '-ERR Unknown error'
    if msg:
        error_msg += f': {msg}\r\n'
    else:
        error_msg += '\r\n'
    return error_msg.encode()


DEBUG = True


class POP3Server(BaseRequestHandler):
    def handle(self):
        conn = self.request
        # handle connection
        conn.sendall(b'+OK POP3 server ready\r\n')

        # verify user and password
        user = None
        while True:
            message = get_message(conn, to_print=DEBUG)
            if message[0].upper() == 'QUIT':
                conn.sendall(b'+OK\r\n')
                return

            if len(message) < 2:
                conn.sendall(pop_error_report(INVALID_COMMAND))
                continue

            if message[0].upper() == 'USER':
                user = message[1]
                if user in ACCOUNTS:
                    conn.sendall(b'+OK\r\n')
                else:
                    conn.sendall(pop_error_report(AUTH_FAILED, 'User not found'))

            elif message[0].upper() == 'PASS':
                if user is None:
                    conn.sendall(pop_error_report(AUTH_FAILED, 'No user specified'))
                elif message[1] == ACCOUNTS[user]:
                    conn.sendall(b'+OK user successfully login\r\n')
                    break
                else:
                    conn.sendall(pop_error_report(AUTH_FAILED, 'Wrong password'))

            else:
                conn.sendall(pop_error_report(INVALID_COMMAND))

        # handle commands
        delete_list = []
        mess_list = MAILBOXES[user]
        while True:
            message = get_message(conn, to_print=DEBUG)
            if len(message) == 0:
                continue

            command = message[0].upper()
            if command == 'STAT':
                mess_num = len(mess_list)
                mess_totalbytes = 0
                for mess in mess_list:
                    # TODO: check if this is correct
                    mess_totalbytes += len(mess)
                conn.sendall(f'+OK {mess_num} {mess_totalbytes}\r\n'.encode())

            elif command == 'LIST':
                len_list = []
                # TODO: figure out what should I send
                for mess in mess_list:
                    len_list.append(len(mess))
                for i in range(len(len_list)):
                    conn.sendall(f'{i + 1} {len_list[i]}\r\n'.encode())

            elif command == 'RETR':
                if len(message) < 2:
                    conn.sendall(pop_error_report(INVALID_COMMAND))
                    continue
                mess_num = int(message[1])
                if mess_num > len(mess_list) or mess_num < 1:
                    conn.sendall(pop_error_report(INVALID_ARGUMENT, 'Message not found'))
                else:
                    conn.sendall(b'+OK\r\n')
                    # TODO: figure out what if it is right
                    conn.sendall(mess_list[mess_num - 1])
                    conn.sendall(b'\r\n.\r\n')

            elif command == 'DELE':
                if len(message) < 2:
                    conn.sendall(pop_error_report(INVALID_COMMAND))
                    continue
                del_num = int(message[1])
                if del_num > len(mess_list) or del_num < 1:
                    conn.sendall(pop_error_report(INVALID_ARGUMENT, 'Message not found'))
                else:
                    delete_list.append(del_num - 1)
                    conn.sendall(b'+OK\r\n')

            elif command == 'RSET':
                delete_list = []
                conn.sendall(b'+OK\r\n')

            elif command == 'NOOP':
                conn.sendall(b'+OK\r\n')

            elif command == 'QUIT':
                delete_list.sort(reverse=True)
                for del_num in delete_list:
                    del MAILBOXES[user][del_num]
                conn.sendall(b'+OK\r\n')
                break
            else:
                conn.sendall(pop_error_report(INVALID_COMMAND))


WAITING_MAIL = 0
WAITING_RCPT = 1
WAITING_DATA = 2

class SMTPServer(BaseRequestHandler):
    def handle(self):
        conn = self.request
        # handle connection
        conn.sendall(b'220 SMTP server ready\r\n')
        message = get_message(conn, to_print=DEBUG)
        if message[0].upper() == 'HELO':
            conn.sendall(b'250 OK\r\n')
        elif message[0].upper() == 'EHLO':
            if len(message) >= 2:
                # TODO: I should sub the ip out
                conn.sendall(b'250 OK\r\n')
            else:
                conn.sendall(b'500 Error: bad syntax\r\n')
                return
        else:
            conn.sendall(b'500 Error: bad syntax\r\n')
            return

        # verify user and password
        # TODO: figure out what should I do

        # receive mail
        send_list = []
        state = WAITING_MAIL
        src = None
        dst = None
        while True:
            message = get_message(conn, to_print=DEBUG)
            if len(message) == 0:
                continue
            command = message[0].upper()

            # TODO: figure out what should I do
            if command == 'QUIT':
                conn.sendall(b'221 Bye\r\n')
                for src, dst, data in send_list:
                    mail_domain = dst.split('@')[-1]
                    server_domain = fdns_query(mail_domain, 'MX')
                    to_port = int(fdns_query(server_domain, 'P'))
                    # TODO: What should be the judgement condition?
                    if to_port == SMTP_PORT:
                        if DEBUG:
                            print("send to myself")
                        MAILBOXES[dst].append(data)
                    else:
                        if DEBUG:
                            print("send to other server")
                        send_mail(to_port, src, dst, data)
                break

            # receive mail
            if state == WAITING_MAIL:
                if len(message) >= 2 and command == 'MAIL' and message[1].startswith('FROM:'):
                    src = message[1][6:len(message[1]) - 1]
                    if DEBUG:
                        print("src: ", src)
                    state = WAITING_RCPT
                    conn.sendall(b'250 OK\r\n')
                else:
                    conn.sendall(b'500 Error: bad syntax\r\n')
                    continue

            elif state == WAITING_RCPT:
                if len(message) >= 2 and command == 'RCPT' and message[1].startswith('TO:'):
                    dst = message[1][4:len(message[1]) - 1]
                    if DEBUG:
                        print("dst: ", dst)
                    state = WAITING_DATA
                    conn.sendall(b'250 OK\r\n')
                else:
                    conn.sendall(b'500 Error: bad syntax\r\n')
                    continue

            elif state == WAITING_DATA:
                if message[0].upper() == 'DATA':
                    conn.sendall(b'354 End data with <CR><LF>.<CR><LF>\r\n')
                    data = conn.recv(1024)
                    while not data.decode().endswith('\r\n.\r\n'):
                        data += conn.recv(1024)
                    print("data: ", data)
                    print("decode data: ", data.decode())
                    conn.sendall(b'250 OK\r\n')
                    send_list.append((src, dst, data))
                    state = WAITING_MAIL
                else:
                    conn.sendall(b'500 Error: bad syntax\r\n')
                    continue


            else:
                conn.sendall(b'500 Error: bad syntax\r\n')
                continue







# TODO: figure out whether it works or not
def send_mail(to_port, src, dst, data):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect(('localhost', to_port))
    conn.sendall(f'HELO {src}\r\n'.encode())
    conn.recv(1024)
    conn.sendall(f'MAIL FROM:<{src}>\r\n'.encode())
    conn.recv(1024)
    conn.sendall(f'RCPT TO:<{dst}>\r\n'.encode())
    conn.recv(1024)
    conn.sendall(b'DATA\r\n')
    conn.recv(1024)
    conn.sendall(data)
    conn.recv(1024)
    conn.sendall(b'QUIT\r\n')
    conn.recv(1024)
    conn.close()


if __name__ == '__main__':

    # print(ACCOUNTS)
    # print(MAILBOXES)
    # print(type(MAILBOXES))

    if student_id() % 10000 == 0:
        raise ValueError('Invalid student ID')

    smtp_server = ThreadingTCPServer(('', SMTP_PORT), SMTPServer)
    pop_server = ThreadingTCPServer(('', POP_PORT), POP3Server)
    Thread(target=smtp_server.serve_forever).start()
    Thread(target=pop_server.serve_forever).start()
