import re
import sys
import getpass
import argparse
from mail import Mail
from pop3 import Pop3

MAIL_LIST = {
    'mail.ru': ('pop.mail.ru', 995),
    'bk.ru': ('pop.mail.ru', 995),
    'inbox.ru': ('pop.mail.ru', 995),
    'list.ru': ('pop.mail.ru', 995),
    'yandex.ru': ('pop.yandex.ru', 995),
    'gmail.com': ('pop.gmail.com', 995),
    'yahoo.com': ('pop.mail.yahoo.com', 995)
}


class ClosedError(Exception):
    pass


class MailClient:
    def __init__(self, address, password, host=None, port=995,
                 attachments=False, messages=False):
        self.address = address
        self.password = password
        self.attachments = attachments
        self.messages = messages
        if host is None:
            return
        self.host = host
        self.port = port
        self.connection = self.connect()
        self.msg_count = int(self.connection.stat().decode().split()[1])

    def __enter__(self):
        sys.stdout.write('Connected to %s\n' % self.connection.host)
        sys.stdout.write('Message count: %d\n' % self.msg_count)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            sys.stderr.write('%s\n' % exc_val)
        self.connection.quit()

    def connect(self):
        """
        Return pop3 connection
        """
        connection = Pop3(self.host, self.port)
        connection.user(self.address)
        connection.pass_(self.password)
        return connection

    def check_mail_number(self, user_input, msg_count=None):
        """
        Checks whether user_input is correct

        :type user_input: str
        :type msg_count: int
        """
        if msg_count is None:
            msg_count = self.msg_count
        try:
            mail_number = int(user_input)
        except ValueError:
            sys.stderr.write('Input int value\n')
            return False
        if mail_number > msg_count or mail_number <= 0:
            sys.stderr.write('Input the number ' +
                             'below %d and above zero\n' % msg_count)
            return False
        return True

    def show_message(self, number):
        try:
            data = b'\n'.join(self.connection.retr(number)[1])
            mail = Mail(data, self.attachments, self.messages)
        except EOFError:
            raise ClosedError('Connection is closed')

        for header in mail.get_headers('Date', 'From', 'To', 'Subject'):
            sys.stdout.write('%s:\n\t%s\n' % header)

        message_lines = mail.get_message().split('\n')
        if not message_lines:
            return

        sys.stdout.write('Message:\n')
        for message_line in message_lines:
            sys.stdout.write('\t%s\n' % message_line)

    def send_short(self, command):
        res = self.connection.short_cmd(command).decode()
        sys.stdout.write('%s\n' % res)

    def send_long(self, command):
        res = self.connection.long_cmd(command)[0].decode()
        sys.stdout.write('%s\n' % res)


def check_address(address):
    """
    Checks if the address is good
    And if the domain in supported servers

    :param address:
    """
    return re.match(r"^[\w\d.+-]+@"
                    r"[a-zA-Z0-9-]+\."
                    r"[a-zA-Z0-9-.]+$", address)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--attachments', action='store_true',
                        help='Save attachments')
    parser.add_argument('-m', '--messages', action='store_true',
                        help='Save messages')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Silent mode')
    parser.add_argument('-t', '--host', type=str,
                        help='Server host')
    parser.add_argument('-p', '--port', type=int,
                        help='Server port')
    parser.add_argument('-c', '--config', type=str,
                        metavar='CFG',
                        help='Configuration file')
    args = parser.parse_args()

    address, password, host, port = '', '', '', 0

    if args.config:
        try:
            with open(args.config, 'r') as f:
                lines = f.readlines()
                count = len(lines)
                if count >= 1:
                    address = lines[0].strip()
                if count >= 2:
                    password = lines[1].strip()
                if count >= 3:
                    host = lines[2].strip()
                if count >= 4:
                    port = int(lines)
        except IOError:
            sys.stderr.write('Cannot load configuration')
        except ValueError:
            sys.stderr.write('Port must be int')

    address = address or input('' if args.quiet else 'Address: ')
    if not check_address(address):
        sys.stderr.write('Incorrect email address\n')
        sys.exit()

    password = password or getpass.getpass('' if args.quiet else 'Password: ')

    domain = address.split('@')[-1]
    from_list = MAIL_LIST.get(domain)

    host = args.host or host
    if not host:
        host = from_list[0] if from_list is not None \
            else input('' if args.quiet else 'Host: ')

    port = args.port or port
    if not port:
        port = from_list[1] if from_list is not None else 995

    try:
        with MailClient(address, password, host, port,
                        args.attachments, args.messages) as client:
            while True:
                if not args.quiet:
                    sys.stdout.write('Input command:\n')
                user_input = input().split()
                length = len(user_input)

                if not length:
                    continue

                command = user_input[0]
                if command == 'quit':
                    if length != 1:
                        continue
                    break
                elif command == 'show':
                    if length != 2:
                        continue
                    number = user_input[1]
                    if not client.check_mail_number(number):
                        continue
                    client.show_message(number)
                    sys.stdout.write('=' * 50 + '\n')
                elif command == 'command':
                    if length < 3:
                        continue
                    user_command = ' '.join(user_input[2:])
                    if user_input[1] == 'long':
                        client.send_long(user_command)
                    elif user_input[1] == 'short':
                        client.send_short(user_command)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()
