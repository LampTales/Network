from __future__ import annotations

from argparse import ArgumentParser
# from email.mime.text import MIMEText
from queue import Queue
import socket
from socketserver import ThreadingTCPServer, BaseRequestHandler
from threading import Thread
import logging

import tomli

def student_id() -> int:
    return 12111519


parser = ArgumentParser()
parser.add_argument('--name', '-n', type=str, required=True)
parser.add_argument('--smtp', '-s', type=int)
parser.add_argument('--pop', '-p', type=int)

args = parser.parse_args()

LOG = False
if LOG:
    log_file = f'{args.name}.log'
    logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

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
    logging.info(message.rstrip('\r\n'))
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
    if to_print and not to_print_ori:
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
        total_len = len(MAILBOXES[user])
        delete_list = []
        left_list = [i for i in range(total_len)]
        mess_list = MAILBOXES[user]
        while True:
            message = get_message(conn, to_print=DEBUG)
            if len(message) == 0:
                continue

            command = message[0].upper()
            if command == 'STAT':
                mess_totalbytes = 0
                for i in left_list:
                    mess_totalbytes -= len(mess_list[i])
                conn.sendall(f'+OK {len(left_list)} {mess_totalbytes}\r\n'.encode())

            elif command == 'LIST':
                conn.sendall(f'+OK {len(left_list)} messages\r\n'.encode())
                for i in left_list:
                    conn.sendall(f'{i + 1} {len(mess_list[i])}\r\n'.encode())
                conn.sendall(b'.\r\n')

            elif command == 'RETR':
                if len(message) < 2:
                    conn.sendall(pop_error_report(INVALID_COMMAND))
                    continue
                mess_num = int(message[1]) - 1
                if mess_num == -1:
                    send_help(conn)
                    continue
                if mess_num not in left_list:
                    conn.sendall(pop_error_report(INVALID_ARGUMENT, 'Message not found'))
                    continue
                else:
                    conn.sendall(b'+OK\r\n')
                    conn.sendall(mess_list[mess_num])

            elif command == 'DELE':
                if len(message) < 2:
                    conn.sendall(pop_error_report(INVALID_COMMAND))
                    continue
                del_num = int(message[1]) - 1
                if del_num not in left_list:
                    conn.sendall(pop_error_report(INVALID_ARGUMENT, 'Message not found'))
                    continue
                else:
                    delete_list.append(del_num)
                    left_list.remove(del_num)
                    conn.sendall(b'+OK\r\n')

            elif command == 'RSET':
                delete_list = []
                left_list = [i for i in range(total_len)]
                conn.sendall(b'+OK\r\n')

            elif command == 'NOOP':
                conn.sendall(b'+OK\r\n')

            elif command == 'HELP':
                send_help(conn)

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
        from_ip = None
        conn.sendall(b'220 SMTP server ready\r\n')
        message = get_message(conn, to_print=DEBUG)
        if message[0].upper() == 'HELO':
            conn.sendall(b'250 OK\r\n')
        elif message[0].upper() == 'EHLO':
            if len(message) >= 2:
                if message[1].startswith('['):
                    from_ip = message[1][1:len(message[1]) - 1]
                conn.sendall(b'250 OK\r\n')
            else:
                conn.sendall(b'500 Error: bad syntax\r\n')
                return
        else:
            conn.sendall(b'500 Error: bad syntax\r\n')
            return

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

            if command == 'QUIT':
                conn.sendall(b'221 Bye\r\n')
                for src, dst, data in send_list:
                    mail_domain = dst.split('@')[-1]
                    server_domain = fdns_query(mail_domain, 'MX')
                    if 'A' not in FDNS or (server_domain+'.') not in FDNS['A']:
                        to_ip = 'localhost'
                    else:
                        to_ip = fdns_query(server_domain, 'A')
                    to_port = int(fdns_query(server_domain, 'P'))
                    if to_ip == 'localhost' and to_port == SMTP_PORT:
                        if DEBUG:
                            print("send to the server itself")
                        MAILBOXES[dst].append(data)
                    else:
                        if DEBUG:
                            print("send to other server")
                            print(f"to_ip: {to_ip}, to_port: {to_port}")
                        send_mail(to_ip, to_port, src, dst, data)
                break

            # receive mail
            if state == WAITING_MAIL:
                if len(message) >= 2 and command == 'MAIL' and message[1].startswith('FROM:'):
                    src = message[1][6:len(message[1]) - 1]
                    if DEBUG:
                        print("src: ", src)
                    from_ip, from_port = analyze_addr(src)
                    if from_ip == 'localhost' and from_port == SMTP_PORT and src not in ACCOUNTS:
                        conn.sendall(b'500 Error: no such account\r\n')
                        continue
                        
                    state = WAITING_RCPT
                    conn.sendall(b'250 OK\r\n')
                else:
                    conn.sendall(b'500 Error: you should send a legal MAIL command\r\n')
                    continue

            elif state == WAITING_RCPT:
                if len(message) >= 2 and command == 'RCPT' and message[1].startswith('TO:'):
                    dst = message[1][4:len(message[1]) - 1]
                    if DEBUG:
                        print("dst: ", dst)

                    # verify user and password
                    if src not in ACCOUNTS and dst not in ACCOUNTS:
                        conn.sendall(b'500 Error: wrong message\r\n')
                        state = WAITING_MAIL
                        continue
                    temp_domain = dst.split('@')[-1] + '.'
                    if temp_domain not in FDNS['MX']:
                        conn.sendall(b'500 Error: unknown domain\r\n')
                        state = WAITING_MAIL
                        continue

                    state = WAITING_DATA
                    conn.sendall(b'250 OK\r\n')
                else:
                    conn.sendall(b'500 Error: you should send a legal RCPT command\r\n')
                    continue

            elif state == WAITING_DATA:
                if message[0].upper() == 'DATA':
                    conn.sendall(b'354 End data with <CR><LF>.<CR><LF>\r\n')
                    data = conn.recv(1024)
                    while not data.decode().endswith('\r\n.\r\n'):
                        data += conn.recv(1024)
                    if DEBUG:
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



def send_mail(to_ip, to_port, src, dst, data):
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((to_ip, to_port))
    get_message(conn, to_print=DEBUG, no_substr=True)
    if DEBUG:
        print(f"start connect with [{to_ip} {to_port}]")
    conn.sendall(f'HELO\r\n'.encode())
    get_message(conn, to_print=DEBUG, no_substr=True)
    conn.sendall(f'MAIL FROM:<{src}>\r\n'.encode())
    get_message(conn, to_print=DEBUG, no_substr=True)
    conn.sendall(f'RCPT TO:<{dst}>\r\n'.encode())
    if DEBUG:
        print("<usr, dst> validation at the other server")
    message = get_message(conn, to_print=DEBUG, to_print_ori=True)
    if message[0] != '250':
        back_mail(src, dst, data)
        conn.sendall(b'QUIT\r\n')
        conn.close()
        return
    conn.sendall(b'DATA\r\n')
    get_message(conn, to_print=DEBUG, no_substr=True)
    conn.sendall(data)
    get_message(conn, to_print=DEBUG, no_substr=True)
    conn.sendall(b'QUIT\r\n')
    get_message(conn, to_print=DEBUG, no_substr=True)
    conn.close()


def analyze_addr(addr):
    smtp_domain = addr.split('@')[-1]
    mail_domain = fdns_query(smtp_domain, 'MX')
    if 'A' not in FDNS or (mail_domain+'.') not in FDNS['A']:
        ip = 'localhost'
    else:
        ip = fdns_query(mail_domain, 'A')
    port = int(fdns_query(mail_domain, 'P'))
    return ip, port


def back_mail(src, dst, data):
    if src in MAILBOXES:
        if DEBUG:
            print(f'back mail from {src} to {dst}')
        MAILBOXES[src].append(data)


def send_help(conn):
    conn.sendall(b'+OK\r\n')
    conn.sendall('STAT: get the number of messages and the total bytes\r\n'.encode())
    conn.sendall('LIST: get the number and size of each message\r\n'.encode())
    conn.sendall('RETR <num>: get the message with the given number\r\n'.encode())
    conn.sendall('DELE <num>: delete the message with the given number\r\n'.encode())
    conn.sendall('RSET: reset the delete list\r\n'.encode())
    conn.sendall('NOOP: return a positive response\r\n'.encode())
    conn.sendall('QUIT: quit the connection\r\n'.encode())
    conn.sendall('HELP: get the help message (RETR 0 can also get help)\r\n'.encode())
    conn.sendall(b'.\r\n')


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
